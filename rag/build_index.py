# ===========================================
# build_index.py — Auto-rebuilding FAISS index
# Rebuilds whenever files in /data change.
# ===========================================

import os
import glob
import json
import hashlib
from typing import Tuple, List

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def _list_data_files(data_dir: str) -> List[str]:
    """Return all files we consider part of the KB."""
    patterns = ("*.pdf", "*.md", "*.txt")
    files = []
    for pat in patterns:
        files.extend(glob.glob(os.path.join(data_dir, pat)))
    return sorted(files)


def get_data_signature(data_dir: str = "data") -> str:
    """
    Create a stable signature (hash) of the current dataset:
      - file paths (relative), sizes, and modified times.
    If anything changes (add/edit/remove), the signature changes.
    """
    os.makedirs(data_dir, exist_ok=True)
    files = _list_data_files(data_dir)
    # Collect metadata that should reflect meaningful changes
    meta = []
    for f in files:
        try:
            stat = os.stat(f)
            meta.append({
                "path": os.path.relpath(f, data_dir).replace("\\", "/"),
                "size": stat.st_size,
                "mtime": int(stat.st_mtime),
            })
        except FileNotFoundError:
            # Ignore races
            continue

    # Hash the JSON dump of metadata (sorted & stable)
    payload = json.dumps(meta, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def _load_docs(data_dir: str = "data"):
    """Load PDFs and text/markdown files from /data into Document objects."""
    docs = []
    for path in _list_data_files(data_dir):
        lower = path.lower()
        if lower.endswith(".pdf"):
            try:
                docs.extend(PyPDFLoader(path).load())
            except Exception:
                # Ignore unreadable PDFs; you may log if desired
                pass
        elif lower.endswith((".md", ".txt")):
            docs.extend(TextLoader(path, encoding="utf-8").load())
    return docs


def _manifest_paths(index_dir: str) -> Tuple[str, str]:
    """Return paths for FAISS index and our manifest metadata."""
    index_path = os.path.join(index_dir, "index.faiss")
    manifest_path = os.path.join(index_dir, "manifest.json")
    return index_path, manifest_path


def _read_manifest(index_dir: str) -> dict:
    """Read the stored manifest (data_signature used to build the index)."""
    _, manifest_path = _manifest_paths(index_dir)
    if not os.path.exists(manifest_path):
        return {}
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_manifest(index_dir: str, data_signature: str, files: List[str]) -> None:
    """Write manifest with current data signature & file list (debug/trace)."""
    os.makedirs(index_dir, exist_ok=True)
    _, manifest_path = _manifest_paths(index_dir)
    payload = {
        "data_signature": data_signature,
        "files": [os.path.basename(f) for f in files],
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def build_or_load_index(
    index_dir: str = "index",
    data_dir: str = "data",
    data_signature: str = None,
    force_rebuild: bool = False,
):
    """
    Load FAISS index if up-to-date; otherwise rebuild it.
    - If data_signature is provided (recommended), we compare it to manifest.
    - 'force_rebuild' lets the UI force a refresh regardless of signature match.
    """
    os.makedirs(index_dir, exist_ok=True)
    index_path, _ = _manifest_paths(index_dir)

    # Compute signature if caller didn't
    if data_signature is None:
        data_signature = get_data_signature(data_dir)

    manifest = _read_manifest(index_dir)
    manifest_sig = manifest.get("data_signature")

    # Decide if we should rebuild
    needs_rebuild = force_rebuild or (manifest_sig != data_signature) or (not os.path.exists(index_path))

    if not needs_rebuild:
        # Fast path: up-to-date -> load existing index
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return FAISS.load_local(
            index_dir,
            embeddings,
            allow_dangerous_deserialization=True
        )

    # Rebuild path
    docs = _load_docs(data_dir)
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(index_dir)

    # Update manifest for future freshness checks
    _write_manifest(index_dir, data_signature, _list_data_files(data_dir))
    return vs
