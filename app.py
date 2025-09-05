# =============================================
# Samukelo's Personal Codex Agent (Streamlit)
# Multi-turn chat + RAG + Hugging Face Inference API (deploy-friendly)
# =============================================

import os
import requests
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
if "model_name" not in st.session_state:
    # logical model key (mapped to a HF model id below)
    st.session_state.model_name = "mistral"


# --------------------------
# Hugging Face Inference API helper
# --------------------------
def call_hf_inference(model_id: str, prompt: str, temperature: float = 0.5, max_new_tokens: int = 400) -> str:
    """
    Calls the Hugging Face Inference API for text generation.
    Requires env var HF_TOKEN to be set (Streamlit Cloud -> App -> Settings -> Secrets).
    """
    hf_token = os.environ.get("HF_TOKEN", "").strip()
    if not hf_token:
        return ("⚠️ Missing HF_TOKEN. Set it in Streamlit Cloud (App → Settings → Secrets).\n"
                "Create a Read token at https://huggingface.co/settings/tokens")

    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": temperature,
            "max_new_tokens": max_new_tokens,
            "return_full_text": False
        }
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # Common successful shape: [{"generated_text": "..."}]
        if isinstance(data, list) and data and isinstance(data[0], dict) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        # Fallback: return raw JSON for debugging
        return str(data)
    except Exception as e:
        return f"⚠️ Hugging Face Inference error: {e}"

# Each logical model key maps to a list of candidate HF repos (first available wins)
HF_MODEL_CANDIDATES = {
    "mistral": [
        "mistralai/Mistral-7B-Instruct-v0.1",   # ✅ public
        "mistralai/Mistral-7B-v0.1",            # ✅ public base
        "tiiuae/falcon-7b-instruct",            # ✅ public
        "google/gemma-2b-it"                    # ✅ light but works
    ],
    "llama3.1": [
        "meta-llama/Meta-Llama-3-8B-Instruct",  # ⚠️ gated, may need acceptance
        "tiiuae/falcon-7b-instruct",            # fallback
        "google/gemma-2b-it"
    ],
    "qwen2.5": [
        "Qwen/Qwen2.5-1.8B-Instruct",           # ✅ small, public
        "Qwen/Qwen1.5-1.8B-Chat",
        "google/gemma-2b-it"
    ],
}

def call_hf_inference_with_fallback(
    logical_key: str,
    prompt: str,
    temperature: float = 0.5,
    max_new_tokens: int = 400
) -> str:
    """
    Try multiple HF models for a given logical key until one works.
    Returns the first successful generated_text or the last error string.
    """
    candidates = HF_MODEL_CANDIDATES.get(logical_key, HF_MODEL_CANDIDATES["mistral"])
    last_err = None
    for model_id in candidates:
        out = call_hf_inference(model_id, prompt, temperature=temperature, max_new_tokens=max_new_tokens)
        # Heuristic: if the response starts with our warning string, it's an error -> try next model
        if not (isinstance(out, str) and out.startswith("⚠️")):
            return out
        last_err = out  # remember the error and try next candidate
    return last_err or "⚠️ All fallback models failed. Try a different model or check HF_TOKEN."

# --------------------------
# Sidebar controls
# --------------------------
with st.sidebar:
    st.header("Settings")

    # Tone/style mode (affects answer instruction)
    st.session_state.mode = st.selectbox(
        "Answer mode",
        list(MODES.keys()),
        index=list(MODES.keys()).index(st.session_state.mode),
        help="Controls tone and structure of the assistant’s answers."
    )

    # Retriever depth
    top_k = st.slider(
        "Retriever k",
        min_value=3,
        max_value=10,
        value=5,
        help="How many chunks to fetch from the index per question."
    )

    # Model picker (maps to HF model IDs below)
    st.session_state.model_name = st.selectbox(
        "Model",
        ["mistral", "llama3.1", "qwen2.5"],
        index=["mistral", "llama3.1", "qwen2.5"].index(st.session_state.model_name),
        help="If Llama is gated, the app will fall back automatically."
    )

    st.markdown("---")
    st.caption("Try a sample question")
    sample = st.selectbox("Samples", ["(Choose)"] + QUESTION_HINTS)
    if sample != "(Choose)":
        st.info(f"Selected sample: {sample}. Type it below or press Enter to send.")

    st.markdown("---")
    # Utility buttons
    
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.session_state.copy_buffer = ""
        st.rerun()
    
    if st.button("Copy last answer"):
        last_ai = next((m for m in reversed(st.session_state.messages) if m["role"] == "assistant"), None)
        st.session_state.copy_buffer = last_ai["content"] if last_ai else ""

    if st.session_state.copy_buffer:
        st.text_area("Copy from here:", st.session_state.copy_buffer, height=120)


# Helpful hint for first-time setup
st.caption("Tip: Add .pdf/.md/.txt files to `data/`. The index auto-refreshes when files change.")


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
st.caption(f"Index status: signature {data_sig[:8]}… (auto-refreshes on file changes)")

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
    for m in recent:
        speaker = "User" if m["role"] == "user" else "Assistant"
        history_lines.append(f"{speaker}: {m['content']}")
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
# Chat input (auto-clears)
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
        retrieved_context, docs = retrieve(vs, user_input, k=top_k)
    except Exception as e:
        with st.chat_message("assistant"):
            st.error("Failed to retrieve context from the index.")
            st.exception(e)
        st.stop()

    # Guard: empty context (no docs yet or no match)
    if not retrieved_context.strip():
        with st.chat_message("assistant"):
            st.info(
                "I didn’t find any matching context in your documents. "
                "Add files to the `data/` folder for better grounded answers."
            )

    # 3) Build prompt text for the model
    prompt_text = build_llm_prompt(
        user_q=user_input,
        retrieved_context=retrieved_context,
        mode_key=st.session_state.mode,
        chat_history=st.session_state.messages,
        max_turns=5
    )

    # 4) Call HF Inference API (deploy-friendly)
    answer = call_hf_inference_with_fallback(
        logical_key=st.session_state.model_name,
        prompt=prompt_text,
        temperature=0.5,
        max_new_tokens=400
    )
    
    # 5) Append assistant response to history and render
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

    # 6) Per-turn retrieved context (collapsible)
    #with st.expander("Retrieved Context"):
    #    st.code(retrieved_context)


# --------------------------
# Regenerate last answer (optional)
# --------------------------
regen = st.button("Regenerate answer for last question")
if regen and len(st.session_state.messages) >= 2:
    # find the most recent user message
    last_user = None
    for m in reversed(st.session_state.messages):
        if m["role"] == "user":
            last_user = m["content"]
            break

    if last_user:
        retrieved_context, docs = retrieve(vs, last_user, k=top_k)
        prompt_text = build_llm_prompt(
            user_q=last_user,
            retrieved_context=retrieved_context,
            mode_key=st.session_state.mode,
            chat_history=st.session_state.messages,
            max_turns=5
        )
        new_answer = call_hf_inference_with_fallback(
            logical_key=st.session_state.model_name,
            prompt=prompt_text,
            temperature=0.5,
            max_new_tokens=400
        )

        # Replace the most recent assistant message content with the new one
        for i in range(len(st.session_state.messages) - 1, -1, -1):
            if st.session_state.messages[i]["role"] == "assistant":
                st.session_state.messages[i]["content"] = new_answer
                break

        st.rerun()


# --------------------------
# Footer
# --------------------------
st.caption(f"Session started: {datetime.now().strftime('%Y-%m-%d')}. Powered by FAISS + HF Inference API.")
