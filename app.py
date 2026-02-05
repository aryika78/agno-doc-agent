import streamlit as st
import tempfile
import os

from agents.orchestrator_agent import OrchestratorAgent
from document_loader import load_document


st.set_page_config(page_title="📄 Document AI Assistant", layout="wide")

st.title("📄 Prompt-Orchestrated Document Assistant")
st.markdown("Chat with your document using the multi-agent AI system")


# ---------------- CACHED DOCUMENT LOADER ----------------
@st.cache_data(show_spinner=False)
def cached_load_document(file_bytes: bytes, suffix: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        temp_path = tmp.name

    try:
        text = load_document(temp_path)
    finally:
        os.remove(temp_path)  # prevent temp file leaks

    return text


# ---------------- SESSION STATE ----------------
if "document_text" not in st.session_state:
    st.session_state.document_text = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_file" not in st.session_state:
    st.session_state.current_file = None


# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload a document (.txt, .pdf, .docx)",
    type=["txt", "pdf", "docx"]
)

if uploaded_file:
    # Detect new file upload
    if st.session_state.current_file != uploaded_file.name:
        suffix = "." + uploaded_file.name.split(".")[-1]

        st.session_state.document_text = cached_load_document(
            uploaded_file.read(),
            suffix
        )

        st.session_state.chat_history = []
        st.session_state.current_file = uploaded_file.name

        st.success("✅ Document loaded successfully!")


st.divider()
st.subheader("💬 Chat with your document")


# ---------------- CHAT UI ----------------
if st.session_state.document_text:

    # 1️⃣ Render full history first
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    # 2️⃣ Take input after rendering
    user_query = st.chat_input("Ask something about the document...")

    # 3️⃣ Process safely
    if user_query:
        st.session_state.chat_history.append(("user", user_query))

        orch = OrchestratorAgent(st.session_state.document_text)
        response = orch.handle(user_query)

        st.session_state.chat_history.append(("assistant", response))

        st.rerun()
