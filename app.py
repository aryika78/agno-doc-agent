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


def prettify_response(content) -> str:
    if isinstance(content, dict):
        return (
            "### ✅ Structured Output\n\n```json\n"
            + json.dumps(content, indent=2)
            + "\n```"
        )

    try:
        data = json.loads(content)
        return (
            "### ✅ Structured Output\n\n```json\n"
            + json.dumps(data, indent=2)
            + "\n```"
        )
    except Exception:
        return content


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
        st.success("✅ All documents cleared (dev mode).")
        st.rerun()

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

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload a document (.txt, .pdf, .docx)",
    type=["txt", "pdf", "docx"],
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_file:
    filename = uploaded_file.name
    file_bytes = uploaded_file.read()
    suffix = "." + filename.split(".")[-1]

    existing_doc_id = store.document_exists(filename)

    if existing_doc_id:
        st.warning(f"⚠ '{filename}' already exists.")
        st.info("Do you want to replace this document?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Yes, replace"):
                document_text = cached_load_document(file_bytes, suffix)

                store.delete_document(existing_doc_id)

                new_doc_id = store.save_document(
                    document_text,
                    metadata={"filename": filename}
                )

                st.session_state.documents[filename] = new_doc_id
                st.session_state.active_doc = new_doc_id
                st.session_state.chat_history = []

                st.session_state.uploader_key += 1
                st.success(f"✅ '{filename}' replaced successfully.")
                st.rerun()

        with col2:
            if st.button("❌ No, keep existing"):
                st.session_state.uploader_key += 1
                st.rerun()

    else:
        document_text = cached_load_document(file_bytes, suffix)

        doc_id = store.save_document(
            document_text,
            metadata={"filename": filename}
        )

        st.session_state.documents[filename] = doc_id
        st.session_state.active_doc = doc_id
        st.session_state.chat_history = []

        st.success(f"✅ '{filename}' indexed and ready!")
        st.rerun()

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

    if st.session_state.active_doc:
        if st.button("🗑️ Delete selected document"):
            filename_to_delete = next(
                name for name, did in st.session_state.documents.items()
                if did == st.session_state.active_doc
            )

            store.delete_document(st.session_state.active_doc)
            del st.session_state.documents[filename_to_delete]

            st.session_state.active_doc = (
                next(iter(st.session_state.documents.values()), None)
            )
            st.session_state.chat_history = []

            st.success(f"🗑️ '{filename_to_delete}' deleted.")
            st.rerun()

st.divider()
st.subheader("💬 Chat with your document")

# ---------------- CHAT UI ----------------
if st.session_state.active_doc:

    for idx, (role, msg) in enumerate(st.session_state.chat_history):
        if role == "assistant" and isinstance(msg, dict):
            content = msg["content"]
            is_json_block = msg["type"] == "json"
        else:
            content = msg
            is_json_block = False

        is_pretty = st.session_state.pretty_flags.get(idx, False)
        display_text = (
            prettify_response(content)
            if (is_json_block and is_pretty)
            else content
        )

        with st.chat_message(role):
            st.markdown(display_text)

        if role == "assistant" and is_json_block:
            label = "🔙 Show Original" if is_pretty else "✨ Prettify Output"
            if st.button(label, key=f"pretty_btn_{idx}"):
                st.session_state.pretty_flags[idx] = not is_pretty
                st.rerun()

    user_query = st.chat_input("Ask something about the document...")

    if user_query:
        st.session_state.chat_history.append(("user", user_query))

        list_keywords = ["extract", "list", "show", "find"]
        top_k = 8 if any(k in user_query.lower() for k in list_keywords) else 5

        context_text = store.search(
            query=user_query,
            top_k=top_k,
            doc_id=st.session_state.active_doc
        )

        orch = OrchestratorAgent(context_text)
        response = orch.handle(user_query) or []

        for block in response:
            st.session_state.chat_history.append(("assistant", block))

        st.rerun()
