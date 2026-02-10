import streamlit as st
import tempfile
import os
import json

from agents.orchestrator_agent import OrchestratorAgent
from document_loader import load_document
from storage.document_store import DocumentStore


def _format_json(content, prettify: bool) -> str:
    """Format dict or JSON string as displayable markdown."""
    data = content if isinstance(content, dict) else json.loads(content)
    json_str = json.dumps(data, indent=2 if prettify else None)
    return f"```json\n{json_str}\n```"


def _is_json_content(msg) -> bool:
    """True if message content is JSON (dict or parseable string)."""
    if not isinstance(msg, dict):
        return False
    c = msg.get("content")
    if isinstance(c, dict):
        return True
    if isinstance(c, str):
        try:
            json.loads(c)
            return True
        except Exception:
            pass
    return False


st.set_page_config(page_title="📄 Document AI Assistant", layout="wide")

st.title("📄 Prompt-Orchestrated Document Assistant")
st.markdown("Chat with your document using the multi-agent AI system")

# ---------------- DOCUMENT STORE ----------------
store = DocumentStore(vector_size=384)

# ---------------- DEV / DEBUG MAINTENANCE ----------------
if os.getenv("DEBUG_RESET") == "true":
    st.divider()
    st.warning("⚠ Dev / Debug only — destructive operation")

    if st.button("🧨 Reset ALL documents (maintenance only)"):
        store.reset_all_documents()
        st.session_state.documents = {}
        st.session_state.active_doc = None
        st.session_state.chat_history = []
        st.session_state.pretty_flags = {}
        st.session_state.uploader_key = 0
        st.success("✅ All documents cleared (dev mode).")
        st.rerun()

# ---------------- CACHED DOCUMENT LOADER ----------------
@st.cache_data(show_spinner=False)
def cached_load_document(file_bytes: bytes, suffix: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        path = tmp.name
    try:
        return load_document(path)
    finally:
        os.remove(path)

# ---------------- SESSION STATE ----------------
if "documents" not in st.session_state:
    st.session_state.documents = store.list_documents()

if "active_doc" not in st.session_state:
    st.session_state.active_doc = (
        next(iter(st.session_state.documents.values()), None)
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pretty_flags" not in st.session_state:
    st.session_state.pretty_flags = {}

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "upload_success_msg" not in st.session_state:
    st.session_state.upload_success_msg = None


# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload a document (.txt, .pdf, .docx)",
    type=["txt", "pdf", "docx"],
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_file:
    filename = uploaded_file.name
    suffix = "." + filename.split(".")[-1]
    file_bytes = uploaded_file.read()

    existing_doc_id = store.document_exists(filename)

    if existing_doc_id:
        st.warning(f"⚠ '{filename}' already exists.")
        st.info("Do you want to replace this document?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Yes, replace"):
                text = cached_load_document(file_bytes, suffix)

                store.delete_document(existing_doc_id)
                new_doc_id = store.save_document(
                    text,
                    metadata={"filename": filename}
                )

                st.session_state.documents[filename] = new_doc_id
                st.session_state.active_doc = new_doc_id
                st.session_state.chat_history = []

                st.session_state.uploader_key += 1
                st.session_state.upload_success_msg = f"✅ '{filename}' indexed and ready!"
                st.rerun()

        with col2:
            if st.button("❌ No, keep existing"):
                # NOTHING changes except uploader reset
                st.session_state.uploader_key += 1
                st.rerun()

    else:
        text = cached_load_document(file_bytes, suffix)

        doc_id = store.save_document(
            text,
            metadata={"filename": filename}
        )

        st.session_state.documents[filename] = doc_id
        st.session_state.active_doc = doc_id
        st.session_state.chat_history = []

        st.session_state.uploader_key += 1
        st.session_state.upload_success_msg = f"✅ '{filename}' indexed and ready!"
        st.rerun()
        
if st.session_state.upload_success_msg:
    st.success(st.session_state.upload_success_msg)
    st.session_state.upload_success_msg = None

# ---------------- DOCUMENT SELECTOR ----------------
if st.session_state.documents:
    st.divider()
    st.subheader("📂 Select Active Document")

    filenames = list(st.session_state.documents.keys())
    selected = st.selectbox(
        "Active document",
        filenames,
        index=filenames.index(
            next(
                name for name, did in st.session_state.documents.items()
                if did == st.session_state.active_doc
            )
        )
    )

    st.session_state.active_doc = st.session_state.documents[selected]

    if st.button("🗑️ Delete selected document"):
        store.delete_document(st.session_state.active_doc)
        del st.session_state.documents[selected]
        st.session_state.active_doc = (
            next(iter(st.session_state.documents.values()), None)
        )
        st.session_state.chat_history = []
        st.rerun()

# ---------------- CHAT ----------------
st.divider()
st.subheader("💬 Chat with your document")

if st.session_state.active_doc:
    for idx, (role, msg) in enumerate(st.session_state.chat_history):
        with st.chat_message(role):
            if role == "assistant" and _is_json_content(msg):
                is_prettified = st.toggle("Prettify JSON", value=True, key=f"prettify_{idx}")
                c = msg["content"]
                data = c if isinstance(c, dict) else json.loads(c)
                st.markdown(_format_json(data, is_prettified))
            elif isinstance(msg, dict):
                st.markdown(msg.get("content", ""))
            else:
                st.markdown(msg)

    query = st.chat_input("Ask something about the document...")
    if query:
        st.session_state.chat_history.append(("user", query))

        q_lower = query.lower()
        top_k = 15 if any(p in q_lower for p in ["list all", "show all"]) else 5
        context = store.search(
            query=query,
            doc_id=st.session_state.active_doc,
            top_k=top_k
        )

        orch = OrchestratorAgent(context)
        response = orch.handle(query) or []

        for block in response:
            st.session_state.chat_history.append(("assistant", block))

        st.rerun()
