import streamlit as st
import tempfile
import os
import json

from agents.orchestrator_agent import OrchestratorAgent
from document_loader import load_document
from storage.document_store import DocumentStore


def is_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except Exception:
        return False


def prettify_response(text: str) -> str:
    try:
        data = json.loads(text)
        return "### ✅ Structured Output\n\n```json\n" + json.dumps(data, indent=2) + "\n```"
    except Exception:
        return text


st.set_page_config(page_title="📄 Document AI Assistant", layout="wide")

st.title("📄 Prompt-Orchestrated Document Assistant")
st.markdown("Chat with your document using the multi-agent AI system")


# ---------------- DOCUMENT STORE ----------------
store = DocumentStore(vector_size=384)


# ---------------- CACHED DOCUMENT LOADER ----------------
@st.cache_data(show_spinner=False)
def cached_load_document(file_bytes: bytes, suffix: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        temp_path = tmp.name

    try:
        text = load_document(temp_path)
    finally:
        os.remove(temp_path)

    return text


# ---------------- SESSION STATE ----------------
if "documents" not in st.session_state:
    # filename -> doc_id
    st.session_state.documents = {}

if "active_doc" not in st.session_state:
    st.session_state.active_doc = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pretty_flags" not in st.session_state:
    st.session_state.pretty_flags = {}


# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload a document (.txt, .pdf, .docx)",
    type=["txt", "pdf", "docx"]
)

if uploaded_file:
    if uploaded_file.name not in st.session_state.documents:
        suffix = "." + uploaded_file.name.split(".")[-1]

        document_text = cached_load_document(
            uploaded_file.read(),
            suffix
        )

        # 🔹 SAVE DOCUMENT TO QDRANT
        doc_id = store.save_document(
            document_text,
            metadata={"filename": uploaded_file.name}
        )

        st.session_state.documents[uploaded_file.name] = doc_id
        st.session_state.active_doc = doc_id
        st.session_state.chat_history = []

        st.success(f"✅ '{uploaded_file.name}' indexed and ready!")

    else:
        st.info("📄 Document already indexed.")


# ---------------- DOCUMENT SELECTOR ----------------
if st.session_state.documents:
    st.divider()
    st.subheader("📂 Select Active Document")

    filenames = list(st.session_state.documents.keys())

    selected_file = st.selectbox(
        "Active document",
        filenames,
        index=filenames.index(
            next(
                name for name, did in st.session_state.documents.items()
                if did == st.session_state.active_doc
            )
        )
    )

    st.session_state.active_doc = st.session_state.documents[selected_file]


st.divider()
st.subheader("💬 Chat with your document")


# ---------------- CHAT UI ----------------
if st.session_state.active_doc:

    # 1️⃣ Render history
    for idx, (role, msg) in enumerate(st.session_state.chat_history):
        is_pretty = st.session_state.pretty_flags.get(idx, False)
        display_text = prettify_response(msg) if (role == "assistant" and is_pretty) else msg

        with st.chat_message(role):
            st.markdown(display_text)

        if role == "assistant" and is_json(msg):
            btn_label = "🔙 Show Original" if is_pretty else "✨ Prettify Output"
            if st.button(btn_label, key=f"pretty_btn_{idx}"):
                st.session_state.pretty_flags[idx] = not is_pretty
                st.rerun()

    # 2️⃣ Input
    user_query = st.chat_input("Ask something about the document...")

    # 3️⃣ Process
    if user_query:
        st.session_state.chat_history.append(("user", user_query))

        # 🔹 RETRIEVE CONTEXT FROM SELECTED DOC
        # 🔹 Dynamic top_k: higher recall for list/entity queries
        list_keywords = ["extract", "list", "show", "find"]
        top_k = 8 if any(k in user_query.lower() for k in list_keywords) else 5

        context_text = store.search(
            query=user_query,
            top_k=top_k,
            doc_id=st.session_state.active_doc
        )
        
        orch = OrchestratorAgent(context_text)
        response = orch.handle(user_query)

        st.session_state.chat_history.append(("assistant", response))
        st.rerun()
