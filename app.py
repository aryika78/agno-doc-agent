import streamlit as st
import tempfile
import os
import json
import re

import plotly.graph_objects as go

from agents.agno_agents import create_document_agent, create_tool_agent
from document_loader import load_document
from storage.document_store import DocumentStore


st.set_page_config(
    page_title="Document AI Assistant",
    page_icon=":page_facing_up:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Custom CSS for a cleaner look (works with both light and dark themes) ----
st.markdown("""
<style>
    /* Tighter top padding */
    .block-container { padding-top: 2rem; }

    /* Suggested-question & follow-up buttons */
    div.stButton > button {
        border-radius: 1rem;
        font-size: 0.85rem;
        padding: 0.4rem 0.9rem;
        transition: all 0.15s ease;
    }
    div.stButton > button:hover {
        border-color: #636EFA;
    }

    /* Chat input area */
    .stChatInput > div { border-radius: 1rem; }

    /* Divider spacing */
    hr { margin: 0.8rem 0; }
</style>
""", unsafe_allow_html=True)

st.title("Document AI Assistant")
st.caption("Upload a document, then chat with it — ask questions, get summaries, extract entities, or visualize data.")

# ---------------- DOCUMENT STORE ----------------
try:
    store = DocumentStore(vector_size=384)
except Exception:
    st.error("Could not connect to Qdrant. Make sure it is running: `docker run -p 6333:6333 qdrant/qdrant`")
    st.stop()

# ---------------- DEV / DEBUG MAINTENANCE ----------------
if os.getenv("DEBUG_RESET") == "true":
    st.divider()
    st.warning("Dev / Debug only")
    if st.button("Reset ALL documents (maintenance only)"):
        store.reset_all_documents()
        for k in ["documents", "active_doc", "chat_history", "uploader_key",
                   "suggested_questions", "doc_insights", "follow_up",
                   "_analyzed_doc_id", "_questions_doc_id"]:
            st.session_state.pop(k, None)
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

for key, default in [
    ("chat_history", []),
    ("uploader_key", 0),
    ("upload_success_msg", None),
    ("suggested_questions", []),
    ("doc_insights", None),
    ("follow_up", None),
    ("_analyzed_doc_id", None),
    ("_questions_doc_id", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ================================================================
#  HELPER — run agent with Azure content-filter retry
# ================================================================
def run_agent(agent, message: str) -> str:
    result = agent.run(message, stream=False)
    content = result.content or ""

    if "content management policy" in content or "content_filter" in content:
        result = agent.run(
            message.replace("USER QUERY:", "USER QUERY: Based on the document,"),
            stream=False,
        )
        content = result.content or ""

    if "content management policy" in content or "content_filter" in content:
        return ""
    return content


def _parse_json(text: str, array: bool = False):
    """Extract JSON object or array from LLM response text."""
    if not text:
        return None
    try:
        pattern = r'\[.*\]' if array else r'\{.*\}'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, TypeError):
        pass
    return None


# ================================================================
#  CHART RENDERING — detect and render chart JSON in responses
# ================================================================
CHART_MARKER = '"chart_type"'

COLORS = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52",
]


def _try_render_chart(text: str) -> bool:
    """If text contains chart JSON, render it and return True."""
    data = _parse_json(text)
    if not data or not isinstance(data, dict) or "chart_type" not in data:
        return False

    chart_type = data.get("chart_type", "").lower()
    title = data.get("title", "")
    items = data.get("data", [])

    # ---- Table ----
    if chart_type == "table":
        columns = data.get("columns", [])
        rows = data.get("rows", [])
        if columns and rows:
            import pandas as pd
            df = pd.DataFrame(rows, columns=columns)
            st.markdown(f"**{title}**" if title else "")
            st.dataframe(df, width="stretch", hide_index=True)
            return True
        return False

    # ---- Timeline / Gantt ----
    if chart_type == "timeline":
        if not items:
            return False
        fig = go.Figure()
        valid_items = [it for it in items if isinstance(it, dict)
                       and it.get("label") and it.get("start") and it.get("end")]
        if not valid_items:
            return False
        for i, item in enumerate(valid_items):
            color = COLORS[i % len(COLORS)]
            fig.add_trace(go.Bar(
                y=[item["label"]],
                x=[_date_diff_months(item["start"], item["end"])],
                base=[_date_to_num(item["start"])],
                orientation="h",
                marker_color=color,
                showlegend=False,
                text=f"{item['start']} — {item['end']}",
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate=f"<b>{item['label']}</b><br>{item['start']} to {item['end']}<extra></extra>",
            ))
        # Build tick labels from the date range
        all_dates = []
        for item in valid_items:
            all_dates.append(_date_to_num(item["start"]))
            all_dates.append(_date_to_num(item["start"]) + _date_diff_months(item["start"], item["end"]))
        min_d, max_d = min(all_dates), max(all_dates)
        tick_vals, tick_text = _generate_date_ticks(min_d, max_d)
        fig.update_layout(
            title=title,
            xaxis=dict(tickvals=tick_vals, ticktext=tick_text),
            margin=dict(t=40, b=40, l=40, r=20),
            height=max(300, len(valid_items) * 50 + 100),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, width="stretch")
        return True

    # ---- Grouped / Stacked bar ----
    if chart_type in ("grouped_bar", "stacked_bar"):
        categories = data.get("categories", [])
        groups = data.get("groups", [])
        if categories and groups:
            barmode = "group" if chart_type == "grouped_bar" else "stack"
            fig = go.Figure()
            for i, grp in enumerate(groups):
                if not isinstance(grp, dict):
                    continue
                fig.add_trace(go.Bar(
                    x=categories,
                    y=grp.get("values", []),
                    name=grp.get("name", f"Group {i+1}"),
                    marker_color=COLORS[i % len(COLORS)],
                ))
            fig.update_layout(
                barmode=barmode,
                title=title,
                margin=dict(t=40, b=40, l=40, r=20),
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, width="stretch")
            return True
        # Fall through to simple bar if groups format not provided
        if not items:
            return False

    # ---- Simple bar / pie ----
    if not items:
        return False

    labels = [item.get("label", "") for item in items if isinstance(item, dict)]
    values = [item.get("value", 0) for item in items if isinstance(item, dict)]

    if not labels or not values:
        return False

    if chart_type == "pie":
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.35,
            textinfo="label+percent",
            marker=dict(colors=COLORS),
        )])
    elif chart_type in ("bar", "horizontal_bar"):
        if chart_type == "horizontal_bar":
            fig = go.Figure(data=[go.Bar(y=labels, x=values, orientation="h",
                                         marker_color="#636EFA")])
        else:
            fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color="#636EFA")])
    else:
        fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color="#636EFA")])

    fig.update_layout(
        title=title,
        margin=dict(t=40, b=40, l=40, r=20),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")
    return True


def _date_to_num(date_str: str) -> float:
    """Convert a date string like '2020-01' or '2020' to months since epoch."""
    parts = date_str.replace("/", "-").split("-")
    try:
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 1
        return year * 12 + month
    except (ValueError, IndexError):
        return 0


def _date_diff_months(start: str, end: str) -> float:
    """Return the difference in months between two date strings."""
    diff = _date_to_num(end) - _date_to_num(start)
    return max(diff, 1)  # at least 1 month wide


def _generate_date_ticks(min_num: float, max_num: float):
    """Generate year-based tick marks for the timeline axis."""
    min_year = int(min_num // 12)
    max_year = int(max_num // 12) + 1
    tick_vals = [y * 12 + 1 for y in range(min_year, max_year + 1)]
    tick_text = [str(y) for y in range(min_year, max_year + 1)]
    return tick_vals, tick_text


def render_message(role: str, msg: str):
    """Render a chat message, handling JSON, charts, and markdown."""
    with st.chat_message(role):
        if role != "assistant":
            st.markdown(msg)
            return

        stripped = msg.strip()

        # Try chart rendering first
        if CHART_MARKER in stripped:
            if _try_render_chart(stripped):
                return

        # Try JSON code block
        if stripped.startswith(("{", "[")):
            try:
                parsed = json.loads(stripped)
                st.code(json.dumps(parsed, indent=2), language="json")
                return
            except (json.JSONDecodeError, TypeError):
                pass

        # Check for mixed content: text + chart JSON
        # Split on the JSON object if chart marker found
        if CHART_MARKER in stripped:
            # Find where the chart JSON starts
            json_start = stripped.find('{"chart_type"')
            if json_start > 0:
                text_part = stripped[:json_start].strip()
                json_part = stripped[json_start:]
                if text_part:
                    st.markdown(text_part)
                _try_render_chart(json_part)
                return

        st.markdown(msg)


# ================================================================
#  FEATURE — Build chat context with history
# ================================================================
def build_chat_input(query: str, history: list, context: str | None = None) -> str:
    """Build the full input message including conversation history."""
    parts = []

    if context:
        parts.append(f"DOCUMENT:\n{context}")

    # Include last 4 exchanges (8 messages) for conversational memory
    recent = history[-8:]
    if recent:
        conv_lines = []
        for role, msg in recent:
            prefix = "User" if role == "user" else "Assistant"
            # Truncate long messages in history to save tokens
            short = msg[:500] + "..." if len(msg) > 500 else msg
            conv_lines.append(f"{prefix}: {short}")
        parts.append("CONVERSATION HISTORY:\n" + "\n".join(conv_lines))

    parts.append(f"USER QUERY: {query}")
    return "\n\n".join(parts)


# ================================================================
#  FEATURE — Suggested questions (auto on upload/switch)
# ================================================================
def generate_suggested_questions(doc_id: str) -> list[str]:
    """Ask the LLM to suggest 5 questions about the document."""
    full_text = store.get_full_text(doc_id)
    agent = create_document_agent()

    prompt = (
        f"DOCUMENT:\n{full_text}\n\n"
        "USER QUERY: Suggest exactly 5 short questions that someone reading this document would want answered. "
        "Rules:\n"
        "- Questions must be about FACTS, DATA, or CONTENT inside the document (names, numbers, events, technologies, dates, comparisons, etc.).\n"
        "- Do NOT suggest meta-questions about improving the document (no 'should the doc add...', 'would it benefit from...', 'could the author...').\n"
        "- Cover diverse topics from different parts of the document — not all about the same thing.\n"
        "- Include 1 question that asks for a visualization or comparison chart of data in the document "
        "(e.g. 'Compare the technologies used across projects as a bar chart').\n"
        "- Keep each question under 15 words.\n"
        "Return ONLY a JSON array of 5 strings, nothing else. "
        'Example: ["What is...?", "Who...?"]'
    )
    raw = run_agent(agent, prompt)
    questions = _parse_json(raw, array=True)
    if isinstance(questions, list):
        return [str(q) for q in questions[:5]]
    return []


# ================================================================
#  FEATURE — Deep insights (button-triggered)
# ================================================================
def generate_doc_insights(doc_id: str) -> dict | None:
    """Extract structured insights from the document."""
    full_text = store.get_full_text(doc_id)
    agent = create_document_agent()

    prompt = (
        f"DOCUMENT:\n{full_text}\n\n"
        "USER QUERY: Analyze this document in two steps.\n\n"
        "STEP 1 — Think about what this document is and what a reader would want to know at a glance. "
        "What are the most important categories of information in THIS specific document? "
        "For example, a hiring contract's key info is parties, compensation, and terms — "
        "while a technical spec's key info is system components, requirements, and constraints. "
        "Every document is different.\n\n"
        "STEP 2 — Extract that information into this JSON structure:\n"
        "{\n"
        '  "document_type": "what this document is",\n'
        '  "title": "descriptive title or subject",\n'
        '  "sections": [\n'
        '    {"label": "Section Name", "items": [\n'
        '      {"title": "Item name", "detail": "1-line description"}\n'
        "    ]}\n"
        "  ],\n"
        '  "highlights": ["most important takeaway 1", "most important takeaway 2", "..."]\n'
        "}\n\n"
        "Rules:\n"
        "- Section labels must be SPECIFIC to this document's content (not generic like 'Key Information' or 'Important Details').\n"
        "- Only include a section if it has real, substantive items from the document.\n"
        "- If an item's value is illegible, garbled, empty, unclear, or not stated — DO NOT include that item at all. Completely omit it. Never say 'not clearly captured', 'garbled', 'not recorded', or 'partially illegible'. If a section has no clean items left after removing unclear ones, drop the entire section.\n"
        "- 3-5 sections, 2-6 items each, 3-5 highlights.\n"
        "- Return ONLY the JSON object, no other text."
    )
    raw = run_agent(agent, prompt)
    return _parse_json(raw)


# ================================================================
#  FEATURE — Follow-up question (auto after each response)
# ================================================================
def generate_follow_up(context: str, history: list) -> str | None:
    """Generate a single follow-up question based on the conversation so far."""
    if not history:
        return None

    agent = create_document_agent()

    # All user questions — covers both "what's been discussed" and "what not to repeat"
    all_user_questions = [msg for role, msg in history if role == "user"]
    asked_list = "\n".join(f"- {q}" for q in all_user_questions)

    prompt = (
        f"DOCUMENT:\n{context}\n\n"
        f"QUESTIONS ALREADY ASKED:\n{asked_list}\n\n"
        "USER QUERY: Suggest exactly 1 short follow-up question based on the document.\n"
        "Rules:\n"
        "- Look at the questions already asked. If they are all about the SAME topic, "
        "suggest a question about a COMPLETELY DIFFERENT part of the document.\n"
        "- If the questions cover varied topics, suggest a natural follow-up to the last one.\n"
        "- The question must be about FACTS or DATA in the document — never about improving/editing the document.\n"
        "- Do NOT suggest anything similar to any question already asked. Check every single one.\n"
        "- Keep it under 15 words. Use 'the document', names, etc. — NOT 'I' or 'my'.\n"
        "Return ONLY the question text, nothing else. No quotes, no prefix."
    )

    result = run_agent(agent, prompt)
    if result:
        result = result.strip().strip('"\'')
        result = re.sub(r'^(follow[- ]?up|next|suggested|question)\s*:\s*', '', result, flags=re.IGNORECASE)
        return result.strip()
    return None


# ================================================================
#  FILE UPLOAD
# ================================================================
def _handle_new_doc(doc_id: str, filename: str):
    """Common state reset + auto-generate questions after upload."""
    st.session_state.documents[filename] = doc_id
    st.session_state.active_doc = doc_id
    st.session_state.chat_history = []
    st.session_state.follow_up = None
    st.session_state.doc_insights = None
    st.session_state._analyzed_doc_id = None
    st.session_state.uploader_key += 1
    st.session_state.upload_success_msg = f"'{filename}' indexed and ready!"

    # Auto-generate suggested questions
    with st.spinner("Generating suggested questions..."):
        st.session_state.suggested_questions = generate_suggested_questions(doc_id)
        st.session_state._questions_doc_id = doc_id


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
        st.warning(f"'{filename}' already exists.")
        st.info("Do you want to replace this document?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, replace"):
                text = cached_load_document(file_bytes, suffix)
                store.delete_document(existing_doc_id)
                new_doc_id = store.save_document(text, metadata={"filename": filename})
                _handle_new_doc(new_doc_id, filename)
                st.rerun()
        with col2:
            if st.button("No, keep existing"):
                st.session_state.uploader_key += 1
                st.rerun()
    else:
        try:
            text = cached_load_document(file_bytes, suffix)
            doc_id = store.save_document(text, metadata={"filename": filename})
            _handle_new_doc(doc_id, filename)
            st.rerun()
        except ValueError as e:
            st.error(f"Could not process '{filename}': {e}")
        except Exception as e:
            st.error(f"Failed to upload '{filename}': {e}")

if st.session_state.upload_success_msg:
    st.success(st.session_state.upload_success_msg)
    st.session_state.upload_success_msg = None


# ================================================================
#  DOCUMENT SELECTOR
# ================================================================
if st.session_state.documents:
    filenames = list(st.session_state.documents.keys())
    active_name = None
    for name, did in st.session_state.documents.items():
        if did == st.session_state.active_doc:
            active_name = name
            break

    selected = st.selectbox(
        "Active document",
        filenames,
        index=filenames.index(active_name) if active_name in filenames else 0
    )

    new_doc_id = st.session_state.documents[selected]
    if new_doc_id != st.session_state.active_doc:
        st.session_state.active_doc = new_doc_id
        st.session_state.chat_history = []
        st.session_state.follow_up = None
        st.session_state.doc_insights = None
        st.session_state.suggested_questions = []
        st.session_state._analyzed_doc_id = None
        st.session_state._questions_doc_id = None
    else:
        st.session_state.active_doc = new_doc_id

    if st.button("Delete selected document", type="secondary"):
        store.delete_document(st.session_state.active_doc)
        del st.session_state.documents[selected]
        st.session_state.active_doc = (
            next(iter(st.session_state.documents.values()), None)
        )
        st.session_state.chat_history = []
        st.session_state.doc_insights = None
        st.session_state.suggested_questions = []
        st.session_state.follow_up = None
        st.session_state._analyzed_doc_id = None
        st.session_state._questions_doc_id = None
        st.rerun()


# ================================================================
#  AUTO — Generate suggested questions on upload/switch
# ================================================================
if (st.session_state.active_doc
        and st.session_state._questions_doc_id != st.session_state.active_doc):
    with st.spinner("Generating suggested questions..."):
        st.session_state.suggested_questions = generate_suggested_questions(
            st.session_state.active_doc
        )
        st.session_state._questions_doc_id = st.session_state.active_doc
    st.rerun()


# ================================================================
#  SIDEBAR — Document Insights (button-triggered)
# ================================================================
with st.sidebar:
    st.markdown("#### Document Insights")
    st.caption("Key information and highlights from your document")
    st.divider()

if st.session_state.active_doc:
    with st.sidebar:
        current_filename = "Document"
        for fname, did in st.session_state.documents.items():
            if did == st.session_state.active_doc:
                current_filename = fname
                break

        insights = st.session_state.doc_insights

        if not insights:
            st.markdown(f"**{current_filename}**")
            st.caption("Click below to extract key insights from this document")
            if st.button("Analyze Document", use_container_width=True):
                with st.spinner("Analyzing document..."):
                    st.session_state.doc_insights = generate_doc_insights(
                        st.session_state.active_doc
                    )
                    st.session_state._analyzed_doc_id = st.session_state.active_doc
                st.rerun()
        else:
            st.markdown(f"**{current_filename}**")
            doc_type = insights.get("document_type") or "document"
            title = insights.get("title") or ""
            st.caption(f"{doc_type.upper()}{'  |  ' + title if title else ''}")

            sections = insights.get("sections") or []
            highlights = insights.get("highlights") or []

            for section in sections:
                if not isinstance(section, dict):
                    continue
                label = section.get("label", "")
                items = section.get("items") or []
                if not label or not items:
                    continue
                with st.expander(f"{label}  ({len(items)})", expanded=False):
                    for item in items:
                        if isinstance(item, dict):
                            st.markdown(f"**{item.get('title', '')}**")
                            detail = item.get("detail", "")
                            if detail:
                                st.caption(detail)
                        elif isinstance(item, str):
                            st.markdown(f"- {item}")

            if highlights:
                with st.expander("Key Highlights", expanded=True):
                    for h in highlights:
                        st.markdown(f"- {h}")


# ================================================================
#  CHAT
# ================================================================
st.divider()
st.subheader("Chat with your document")

if not st.session_state.active_doc:
    st.info("Upload a document above to start chatting.")

if st.session_state.active_doc:

    # --- Suggested Questions (auto-generated, shown before chat starts) ---
    if st.session_state.suggested_questions and not st.session_state.chat_history:
        st.markdown("**Try asking:**")
        questions = st.session_state.suggested_questions
        for row_start in range(0, len(questions), 3):
            row = questions[row_start:row_start + 3]
            cols = st.columns(len(row))
            for i, q in enumerate(row):
                idx = row_start + i
                with cols[i]:
                    if st.button(q, key=f"sq_{idx}", use_container_width=True):
                        st.session_state.chat_history.append(("user", q))
                        st.session_state._pending_query = q
                        st.rerun()

    # --- Display chat history ---
    for role, msg in st.session_state.chat_history:
        render_message(role, msg)

    # --- Follow-up question suggestion (after conversation starts) ---
    if st.session_state.follow_up and st.session_state.chat_history:
        fu = st.session_state.follow_up
        st.markdown("**You might also ask:**")
        if st.button(fu, key="follow_up_btn", use_container_width=True):
            st.session_state.chat_history.append(("user", fu))
            st.session_state._pending_query = fu
            st.session_state.follow_up = None
            st.rerun()

    # --- Handle query ---
    pending = st.session_state.pop("_pending_query", None)
    query = st.chat_input("Ask something about the document...")
    active_query = pending or query

    if active_query:
        if not pending:
            st.session_state.chat_history.append(("user", active_query))

        with st.spinner("Thinking..."):
            # Tool-based agent — it fetches its own context from the document
            agent = create_tool_agent(st.session_state.active_doc, store)
            input_msg = build_chat_input(
                active_query, st.session_state.chat_history[:-1]
            )
            content = run_agent(agent, input_msg)

            if not content:
                content = "Sorry, I couldn't process that query. Please try rephrasing your question."

            st.session_state.chat_history.append(("assistant", content))

            # Generate follow-up suggestion (full text so agent can pivot to unexplored topics)
            full_text = store.get_full_text(st.session_state.active_doc)
            follow_up = generate_follow_up(full_text, st.session_state.chat_history)
            st.session_state.follow_up = follow_up

        st.rerun()
