import streamlit as st
import tempfile
from agents.orchestrator_agent import OrchestratorAgent
from document_loader import load_document

st.set_page_config(page_title="📄 Document AI Assistant", layout="wide")

st.title("📄 Prompt-Orchestrated Document Assistant")
st.sidebar.title("ℹ️ How this works")
st.sidebar.markdown("""
- Multi-Agent Document AI
- Intent detection + agent orchestration
- Works on PDF / DOCX / TXT
- Shows explainable AI logs in terminal
""")

st.markdown("Chat with your document using the multi-agent AI system")

# ---------------- SESSION STATE ----------------
if "document_text" not in st.session_state:
    st.session_state.document_text = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload a document (.txt, .pdf, .docx)",
    type=["txt", "pdf", "docx"]
)

if uploaded_file:
    suffix = "." + uploaded_file.name.split(".")[-1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    st.session_state.document_text = load_document(temp_path)
    st.session_state.chat_history = []
    st.success("✅ Document loaded successfully!")

st.divider()
st.subheader("💬 Chat with your document")

# ---------------- CHAT UI ----------------
if st.session_state.document_text:

    # ✅ SHOW FULL CHAT HISTORY FIRST
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    # ✅ THEN TAKE NEW INPUT
    user_query = st.chat_input("Ask something about the document...")

    if user_query:
        orch = OrchestratorAgent(st.session_state.document_text)
        response = orch.handle(user_query)

        st.session_state.chat_history.append(("user", user_query))
        st.session_state.chat_history.append(("assistant", response))

        # Rerun to immediately show the new message
        st.rerun()
