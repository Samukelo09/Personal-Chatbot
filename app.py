# =============================================
# Samukelo's Personal Codex Agent (Streamlit)
# Multi-turn chat + RAG + Ollama (local, free)
# =============================================

import io
import json
from datetime import datetime
import streamlit as st

# RAG helpers (ensure these files exist in rag/)
from rag.build_index import build_or_load_index, get_data_signature
from rag.retriever import retrieve
from rag.prompts import BASE_SYSTEM, MODES, QUESTION_HINTS

# LLM (Ollama) via LangChain
from langchain.schema import SystemMessage, HumanMessage
from langchain_community.chat_models import ChatOllama


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
    st.session_state.model_name = "mistral"  # default Ollama model


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

    # Choose local Ollama model
    st.session_state.model_name = st.selectbox(
        "Model (Ollama)",
        ["mistral", "llama3.1", "qwen2.5:3b-instruct"],
        index=["mistral", "llama3.1", "qwen2.5:3b-instruct"].index(st.session_state.model_name),
        help="Run `ollama pull <model>` beforehand."
    )

    st.markdown("---")
    st.caption("Try a sample question")
    sample = st.selectbox("Samples", ["(Choose)"] + QUESTION_HINTS)
    if sample != "(Choose)":
        st.info(f"Selected sample: {sample}. Type it below or just press Enter to send.")

    st.markdown("---")
    # Utility buttons in three columns
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.session_state.copy_buffer = ""
        st.experimental_rerun()
    
    # Copy last answer helper: places last AI message into a read-only textarea you can Ctrl+C
    if st.button("Copy last answer"):
        last_ai = next(
            (m for m in reversed(
                st.session_state.get("messages", [])
            ) if m["role"] == "assistant"),
            None
        )
        st.session_state.copy_buffer = last_ai["content"] if last_ai else ""
    if st.session_state.copy_buffer:
        st.text_area("Copy from here:", st.session_state.copy_buffer, height=120)



# Helpful hint for first-time setup
st.caption("Tip: Add .pdf/.md/.txt files to `data/` and restart the app to update the index.")


# --------------------------
# Index: build or load once
# --------------------------
@st.cache_resource
# ---- Index: build or load once, keyed by data signature ----
@st.cache_resource
def _load_vs(signature: str, force: bool = False):
    # force lets us explicitly rebuild from the UI
    return build_or_load_index(
        index_dir="index",
        data_dir="data",
        data_signature=signature,
        force_rebuild=force,
    )

# Compute signature on every run (fast)
data_sig = get_data_signature("data")

# A little status text
st.caption(f"Index status: signature {data_sig[:8]}… (auto-refreshes on file changes)")

if st.sidebar.button("Rebuild index now"):
    # force rebuild just for this run
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
# Helper: instantiate the LLM
# --------------------------
def get_llm():
    """Return a ChatOllama instance configured from sidebar settings."""
    return ChatOllama(
        model=st.session_state.model_name,  # "mistral", "llama3.1", ...
        temperature=0.5,
        base_url="http://localhost:11434"
    )


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
                "Add files to the `data/` folder and restart the app for better grounded answers."
            )

    # 3) Build messages for the LLM
    system_msg = SystemMessage(
        content="You are Samukelo's Personal Codex Agent. Be accurate, concise, and cite snippets from CONTEXT when relevant."
    )
    prompt_text = build_llm_prompt(
        user_q=user_input,
        retrieved_context=retrieved_context,
        mode_key=st.session_state.mode,
        chat_history=st.session_state.messages,
        max_turns=5
    )
    human_msg = HumanMessage(content=prompt_text)

    # 4) Query Ollama (local LLM)
    llm = get_llm()

    # 5) Generate answer and display
    try:
        response = llm.invoke([system_msg, human_msg])
        answer = response.content
    except Exception as e:
        answer = (
            "⚠️ I couldn't reach the local model.\n"
            "Make sure Ollama is running and the model is pulled:\n"
            "- Start server: `ollama serve`\n"
            "- Pull model: `ollama pull " + st.session_state.model_name + "`\n"
        )

    # 6) Append assistant response to history and render
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
        # quick, lightweight “sources used”
        if docs:
            st.caption("Sources used: " + ", ".join([f"[Doc {i+1}]" for i in range(len(docs))]))

    # 7) Per-turn retrieved context (collapsible)
    with st.expander("Retrieved Context"):
        st.code(retrieved_context)


# --------------------------
# Regenerate last answer (optional)
# --------------------------
# Button to re-generate the assistant's last response using the last user message
regen = st.button("🔁 Regenerate answer for last question")
if regen and len(st.session_state.messages) >= 2:
    # Last turn should be: ... user, assistant
    last_user = None
    # Scan backwards to find the most recent user message
    for m in reversed(st.session_state.messages):
        if m["role"] == "user":
            last_user = m["content"]
            break

    if last_user:
        # Fetch context again (could change after editing docs)
        retrieved_context, docs = retrieve(vs, last_user, k=top_k)

        system_msg = SystemMessage(
            content="You are Samukelo's Personal Codex Agent. Be accurate, concise, and cite snippets from CONTEXT when relevant."
        )
        prompt_text = build_llm_prompt(
            user_q=last_user,
            retrieved_context=retrieved_context,
            mode_key=st.session_state.mode,
            chat_history=st.session_state.messages,
            max_turns=5
        )
        human_msg = HumanMessage(content=prompt_text)

        llm = get_llm()
        try:
            response = llm.invoke([system_msg, human_msg])
            new_answer = response.content
        except Exception:
            new_answer = (
                "⚠️ I couldn't reach the local model to regenerate. "
                "Ensure Ollama is running and the selected model is available."
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
st.caption(f"Session started: {datetime.now().strftime('%Y-%m-%d')}. Powered by FAISS + Ollama.")
