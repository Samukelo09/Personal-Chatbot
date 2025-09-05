# =============================================
# Samukelo's Personal Codex Agent (Streamlit)
# Multi-turn chat + RAG + Gemini API (deploy-friendly)
# =============================================

import os
import google.generativeai as genai
import re
from datetime import datetime
import streamlit as st

# RAG helpers (ensure these files exist in rag/)
from rag.build_index import build_or_load_index, get_data_signature   # auto-rebuild enabled
from rag.retriever import retrieve
from rag.prompts import BASE_SYSTEM, MODES, QUESTION_HINTS


# --------------------------
# Page setup
# --------------------------
st.set_page_config(page_title="Personal Codex", page_icon="💬")
st.title("Samukelo’s Personal Codex Agent")


# --------------------------
# Session state defaults
# --------------------------
if "messages" not in st.session_state:
    # conversation history: list of {"role": "user"|"assistant", "content": str}
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "Interview mode"
if "copy_buffer" not in st.session_state:
    st.session_state.copy_buffer = ""


# --------------------------
# Gemini API helper
# --------------------------
def call_gemini(prompt: str, model: str = "gemini-2.0-flash") -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return "⚠️ Missing GEMINI_API_KEY. Set it in Streamlit Cloud → Secrets."
    try:
        genai.configure(api_key=key)
        m = genai.GenerativeModel(model)
        resp = m.generate_content(prompt)
        return resp.text or ""
    except Exception as e:
        return f"⚠️ Gemini error: {e}"

# --------------------------
# Sidebar controls
# --------------------------
with st.sidebar:
    st.header("Settings")

    # Tone/style mode (affects answer instruction)
    st.session_state.mode = st.selectbox(
        "Answer mode",
        list(MODES.keys()),
        index=list(MODES.keys()).index(st.session_state.mode)
    )

    # Retriever depth
    top_k = st.slider(
        "Retriever k",
        min_value=3,
        max_value=10,
        value=5
    )

    st.markdown("---")
    st.caption("Try a sample question")
    sample = st.selectbox("Samples", ["(Choose)"] + QUESTION_HINTS)
    if sample != "(Choose)":
        st.info(f"Selected sample: {sample}. Type it below or press Enter to send.")

    st.markdown("---")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.session_state.copy_buffer = ""
        st.rerun()
    
    if st.button("Copy last answer"):
        last_ai = next((m for m in reversed(st.session_state.messages) if m["role"] == "assistant"), None)
        st.session_state.copy_buffer = last_ai["content"] if last_ai else ""

    if st.session_state.copy_buffer:
        st.text_area("Copy from here:", st.session_state.copy_buffer, height=120)

_CIT_PATTERNS = [
    r"\(\s*Doc[s]?\s*[\d,\s]+\)",
    r"\[\s*Doc[s]?\s*[\d,\s]+\s*\]",
    r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]",
    r"\(\s*\d+(?:\s*,\s*\d+)*\s*\)",
]
def clean_answer(text: str) -> str:
    for pat in _CIT_PATTERNS:
        text = re.sub(pat, "", text)
    # remove double spaces left behind
    return re.sub(r"\s{2,}", " ", text).strip()
# --------------------------
# Index: build or load once, keyed by data signature
# --------------------------
@st.cache_resource
def _load_vs(signature: str, force: bool = False):
    return build_or_load_index(
        index_dir="index",
        data_dir="data",
        data_signature=signature,
        force_rebuild=force,
    )

# Compute signature on every run (fast)
data_sig = get_data_signature("data")
#st.caption(f"Index status: signature {data_sig[:8]}…")

# Rebuild button
if st.sidebar.button("Rebuild index now"):
    vs = _load_vs(data_sig, force=True)
    st.sidebar.success("Index rebuilt.")
else:
    vs = _load_vs(data_sig, force=False)


# --------------------------
# Prompt builder
# --------------------------
def build_llm_prompt(
    user_q: str,
    retrieved_context: str,
    mode_key: str,
    chat_history: list[dict],
    max_turns: int = 5
) -> str:
    """
    Creates the prompt for the LLM.
    - Injects BASE_SYSTEM and the selected stylistic MODE.
    - Includes the last `max_turns` of chat for light conversational memory.
    - Adds retrieved context and current user question.
    """
    style = MODES[mode_key]

    # Keep just the last N turns (each turn ~ user+assistant)
    recent = chat_history[-max_turns * 2:]
    history_lines = []
    history_lines = [
        f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}" for m in recent
    ]
    history_text = "\n".join(history_lines) if history_lines else "(no previous turns)"

    return f"""{BASE_SYSTEM}

STYLE: {style}

RECENT CHAT (for continuity):
\"\"\"
{history_text}
\"\"\"

CONTEXT (from Samukelo's docs):
\"\"\"
{retrieved_context}
\"\"\"

CURRENT QUESTION:
{user_q}

Answer as Samukelo (first-person). Be specific and grounded in the CONTEXT when applicable.
If the answer is not in context, say so briefly and avoid fabrications.
"""

# --------------------------
# Render chat history
# --------------------------
for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])


# --------------------------
# Chat input
# --------------------------
placeholder = sample if sample != "(Choose)" else "Ask something like: What kind of engineer are you?"
user_input = st.chat_input(placeholder=placeholder)

# If user submits a message
if user_input:
    # 1) Append user's message to history and render immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2) Retrieve context from FAISS for this question
    try:
        retrieved_context, _ = retrieve(vs, user_input, k=top_k)
    except Exception as e:
        with st.chat_message("assistant"):
            st.error("Failed to retrieve context from the index.")
            st.exception(e)
        st.stop()

    # 3) Build prompt text for the model
    prompt_text = build_llm_prompt(
        user_q=user_input,
        retrieved_context=retrieved_context,
        mode_key=st.session_state.mode,
        chat_history=st.session_state.messages,
        max_turns=5
    )

    # 4) Call Gemini API
    answer = call_gemini(prompt_text)
    answer = clean_answer(answer)
    
    # 5) Append assistant response to history and render
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

    # 6) Per-turn retrieved context (collapsible)
    #with st.expander("Retrieved Context"):
    #    st.code(retrieved_context)




# --------------------------
# Footer
# --------------------------
st.caption(f"Session started: {datetime.now().strftime('%Y-%m-%d')}. Powered by FAISS + HF Inference API.")
