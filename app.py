import streamlit as st
import os
from src.document_processor import DocumentProcessor
from src.qa_agent import QAAgent
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# check if OPENAI_API_KEY is set
if not os.getenv("OPENAI_API_KEY"):
    st.error("Please set the OPENAI_API_KEY environment variable in your .env file.")
    st.stop()

# initialize DocumentProcessor and QAAgent
if "agent" not in st.session_state:
    st.session_state.agent = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed" not in st.session_state:
    st.session_state.processed = False

# app title
st.title("Personal Codex Agent")
st.caption("Chat with an AI assistant that knows about your background and experiences.")

# sidebar for mode selection and document processing
with st.sidebar:
    st.header("Configuration")

    # mode selection
    mode = st.selectbox(
        "Select Mode", 
        ["default", "interview", "storytelling", "creative"]
    )
    
    if st.button("Process Documents") and not st.session_state.processed:
        with st.spinner("Processing documents... This may take a few minutes."):
            prosessor = DocumentProcessor()
            prosessor.process_documents()
            st.session_state.processed = True
            st.success("Documents processed and vector store created.")
        
    # initialize agent button
    if st.button("Initialize AI Agent"):
        with st.spinner("Initializing agent..."):
            st.session_state.agent = QAAgent(mode=mode)
            st.success(f"Agent initialized in {mode} mode.")

    # clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        if st.session_state.agent:
            st.session_state.agent.clear_memory()
        st.rerun()

# display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# chat input
if prompt := st.chat_input("Ask me anything about my background..."):
    # add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # display assstant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        if st.session_state.agent:
            try:
                full_response = st.session_state.agent.ask_question(prompt)
                message_placeholder.markdown(full_response)

            except Exception as e:
                message_placeholder.markdown(f"Error: {str(e)}")
                full_response = f"Error: {str(e)}"

        else:
            warning_msg = "Please initialize the AI agent first from the sidebar."
            message_placeholder.markdown(warning_msg)
            full_response = warning_msg

    # add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    
        