# ===========================================
# build_index.py — Auto-rebuilding FAISS index
# Resilient loaders + rebuilds when /data changes.
# ===========================================

import os
import glob
import json
import hashlib
from typing import Tuple, List

# Try to import LangChain loaders; fall back if unavailable.
try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    _HAS_LC_LOADERS = True
except Exception:
    _HAS_LC_LOADERS = False

from langchain_text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# -------- utilities for data fingerprinting --------

def _list_data_files(data_dir: str) -> List[str]:
    patterns = ("*.pdf", "*.md", "*.txt")
    files = []
    for pat in patterns:
        files.extend(glob.glob(os.path.join(data_dir, pat)))
    return sorted(files)

def get_data_signature(data_dir: str = "data") -> str:
    os.makedirs(data_dir, exist_ok=True)
    files = _list_data_files(data_dir)
    meta = []
    for f in files:
        try:
            st = os.stat(f)
            meta.append({
                "path": os.path.relpath(f, data_dir).replace("\\", "/"),
                "size": st.st_size,
                "mtime": int(st.st_mtime),
            })
        except FileNotFoundError:
            continue
    payload = json.dumps(meta, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(payload.encode("utf-8")).hexdigest()

def _manifest_paths(index_dir: str) -> Tuple[str, str]:
    return os.path.join(index_dir, "index.faiss"), os.path.join(index_dir, "manifest.json")

def _read_manifest(index_dir: str) -> dict:
    _, manifest_path = _manifest_paths(index_dir)
    if not os.path.exists(manifest_path):
        return {}
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _write_manifest(index_dir: str, data_signature: str, files: List[str]) -> None:
    os.makedirs(index_dir, exist_ok=True)
    _, manifest_path = _manifest_paths(index_dir)
    payload = {
        "data_signature": data_signature,
        "files": [os.path.basename(f) for f in files],
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

# -------- resilient document loading --------

def _load_docs_via_langchain(paths: List[str]):
    docs = []
    for path in paths:
        lower = path.lower()
        if lower.endswith(".pdf"):
            try:
                docs.extend(PyPDFLoader(path).load())
            except Exception:
                # ignore unreadable PDFs
                pass
        elif lower.endswith((".md", ".txt")):
            try:
                docs.extend(TextLoader(path, encoding="utf-8").load())
            except Exception:
                pass
    return docs

def _load_docs_via_fallback(paths: List[str]):
    """Fallback loader that does not rely on langchain loaders."""
    from langchain.schema import Document
    docs = []
    for path in paths:
        lower = path.lower()
        if lower.endswith(".pdf"):
            # use pypdf to read text
            try:
                from pypdf import PdfReader
                reader = PdfReader(path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                if text.strip():
                    docs.append(Document(page_content=text, metadata={"source": os.path.basename(path)}))
            except Exception:
                pass
        elif lower.endswith((".md", ".txt")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                if text.strip():
                    docs.append(Document(page_content=text, metadata={"source": os.path.basename(path)}))
            except Exception:
                pass
    return docs

def _load_docs(data_dir: str = "data"):
    paths = _list_data_files(data_dir)
    if _HAS_LC_LOADERS:
        docs = _load_docs_via_langchain(paths)
        # If LC loaders returned nothing (unlikely), try fallback
        if docs:
            return docs
    return _load_docs_via_fallback(paths)

# -------- main build / load --------

def build_or_load_index(
    index_dir: str = "index",
    data_dir: str = "data",
    data_signature: str = None,
    force_rebuild: bool = False,
):
    os.makedirs(index_dir, exist_ok=True)
    index_path, _ = _manifest_paths(index_dir)

    if data_signature is None:
        data_signature = get_data_signature(data_dir)

    manifest = _read_manifest(index_dir)
    manifest_sig = manifest.get("data_signature")

    needs_rebuild = force_rebuild or (manifest_sig != data_signature) or (not os.path.exists(index_path))

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if not needs_rebuild:
        return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)

    # Build fresh
    docs = _load_docs(data_dir)
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks = splitter.split_documents(docs)

    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(index_dir)
    _write_manifest(index_dir, data_signature, _list_data_files(data_dir))
    return vs

