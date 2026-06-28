import html
import re
import streamlit as st
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# Matches:
#  - full URLs with http(s)://
#  - bare "www.xxx.com" domains
#  - bare "xxx.com/..." domains (common TLDs) without a scheme or www
URL_PATTERN = re.compile(
    r'((?:https?://|www\.)[^\s<>"\')\]]+'
    r'|\b[a-zA-Z0-9-]+\.(?:com|org|net|io|gov|edu|co)(?:/[^\s<>"\')\]]*)?)',
    re.IGNORECASE,
)


def linkify(text: str) -> str:
    """Convert bare URLs / domains in plain text into clickable <a> tags."""
    if not text:
        return text

    escaped_text = html.escape(text)

    def _wrap(match: "re.Match") -> str:
        url = match.group(1)
        href = url if url.startswith("http") else f"https://{url}"
        display = html.escape(url)
        return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{display}</a>'

    return URL_PATTERN.sub(_wrap, escaped_text)

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Research Pipeline",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# THEME / GLOBAL CSS
# Palette: midnight slate base, amber primary accent, teal secondary accent.
# Fraunces for display headings, Inter for body/UI, JetBrains Mono for data.
# =============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,600&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg: #0F1117;
        --panel: #171a23;
        --panel-alt: #1c202c;
        --panel-border: #262b38;
        --amber: #E8A33D;
        --teal: #3FBFA8;
        --text: #ECE9E2;
        --text-dim: #9098A8;
    }

    .stApp {
        background: radial-gradient(circle at 15% 0%, #1a1d28 0%, var(--bg) 55%);
        font-family: 'Inter', sans-serif;
        color: var(--text);
    }

    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    section[data-testid="stSidebar"] {
        background: var(--panel);
        border-right: 1px solid var(--panel-border);
    }
    section[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }

    /* ---------- Masthead ---------- */
    .masthead .eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        color: var(--amber);
        text-transform: uppercase;
    }
    .masthead h1 {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 2.2rem;
        margin: 4px 0 2px 0;
        color: var(--text);
        line-height: 1.1;
    }
    .masthead .tagline { font-size: 0.95rem; color: var(--text-dim); }

    /* ---------- Generic card ---------- */
    .ui-card {
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-radius: 14px;
        padding: 20px 22px;
        height: 100%;
    }
    .ui-card.alt { background: var(--panel-alt); }
    .ui-card .card-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-dim);
        margin-bottom: 6px;
    }
    .ui-card .card-value {
        font-family: 'Fraunces', serif;
        font-size: 1.5rem;
        color: var(--text);
    }
    .ui-card .card-value.amber { color: var(--amber); }
    .ui-card .card-value.teal { color: var(--teal); }

    /* ---------- Stage pills ---------- */
    .stage-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.74rem;
        padding: 8px 0;
        text-align: center;
        border-radius: 10px;
        border: 1px solid var(--panel-border);
        color: var(--text-dim);
        background: var(--panel-alt);
        transition: all 0.25s ease;
    }
    .stage-pill.active {
        border-color: var(--amber);
        color: var(--amber);
        box-shadow: 0 0 0 1px rgba(232,163,61,0.25), 0 0 14px rgba(232,163,61,0.18);
    }
    .stage-pill.done { border-color: var(--teal); color: var(--teal); }
    .stage-pill.pending { opacity: 0.55; }

    /* ---------- Inputs ---------- */
    .stTextInput input, .stTextArea textarea {
        background: var(--panel-alt) !important;
        border: 1px solid var(--panel-border) !important;
        color: var(--text) !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
    }
    .stTextInput input:focus { border-color: var(--amber) !important; box-shadow: 0 0 0 1px var(--amber) !important; }
    label, .stTextInput label p, .stSelectbox label p { color: var(--text-dim) !important; font-size: 0.85rem !important; }

    /* ---------- Buttons ---------- */
    div[data-testid="stFormSubmitButton"] button,
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, var(--amber), #c9842a) !important;
        color: #161310 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        width: 100%;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stFormSubmitButton"] button:hover,
    .stButton button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(232,163,61,0.3);
    }
    .stButton button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid var(--panel-border) !important;
        color: var(--text-dim) !important;
        border-radius: 10px !important;
        width: 100%;
    }
    .stButton button[kind="secondary"]:hover { border-color: var(--teal) !important; color: var(--teal) !important; }

    /* ---------- Status / expander ---------- */
    div[data-testid="stStatusWidget"], div[data-testid="stExpander"] {
        background: var(--panel) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 12px !important;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--panel-border); }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-dim);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] { color: var(--amber) !important; border-bottom: 2px solid var(--amber) !important; }

    /* ---------- Content card (report / critic) ---------- */
    .content-card {
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-radius: 14px;
        padding: 28px 32px;
        line-height: 1.65;
    }
    .content-card h1, .content-card h2, .content-card h3 { font-family: 'Fraunces', serif; color: var(--amber); }
    .content-card a { color: var(--teal); }

    .raw-block {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: var(--text-dim);
        white-space: pre-wrap;
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-radius: 10px;
        padding: 18px;
        max-height: 420px;
        overflow-y: auto;
    }

    .stDownloadButton button {
        background: transparent !important;
        border: 1px solid var(--teal) !important;
        color: var(--teal) !important;
        border-radius: 10px !important;
        width: 100%;
    }
    .stDownloadButton button:hover { background: rgba(63,191,168,0.1) !important; }

    hr { border-color: var(--panel-border) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# SESSION STATE
# =============================================================================
def init_state():
    defaults = {"state": None, "topic": "", "history": [], "stage_idx": -1}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

STAGES = ["Search", "Read", "Write", "Critique"]


# =============================================================================
# COMPONENTS
# =============================================================================
def card(label: str, value: str, accent: str = "") -> str:
    """Return HTML for a small stat card."""
    accent_cls = f" {accent}" if accent else ""
    return (
        f'<div class="ui-card"><div class="card-label">{label}</div>'
        f'<div class="card-value{accent_cls}">{value}</div></div>'
    )


def render_stage_rail(active_index: int, container):
    cols = container.columns(len(STAGES))
    for i, (col, name) in enumerate(zip(cols, STAGES)):
        if i < active_index:
            cls = "done"
        elif i == active_index:
            cls = "active"
        else:
            cls = "pending"
        col.markdown(
            f'<div class="stage-pill {cls}">{i+1:02d} · {name}</div>',
            unsafe_allow_html=True,
        )


def run_pipeline_with_ui(topic: str):
    """Runs the 4-stage pipeline, updating the stage rail + status log live."""
    stage_rail_slot = st.empty()
    status_box = st.status("Starting pipeline...", expanded=True)
    render_stage_rail(0, stage_rail_slot)

    state = {}
    try:
        status_box.update(label="Running search agent...")
        status_box.write("🔎 Searching the web for recent, relevant sources...")
        search_agent = build_search_agent()
        search_result = search_agent.invoke(
            {"messages": [("user", f"Find recent, relatable and detailed information about: {topic}")]}
        )
        state["search_results"] = search_result["messages"][-1].content
        status_box.write("✅ Search complete.")
        render_stage_rail(1, stage_rail_slot)

        status_box.update(label="Running reader agent...")
        status_box.write("📖 Scraping the most relevant source for deeper content...")
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"Pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{state['search_results'][:800]}",
                    )
                ]
            }
        )
        state["scraped_content"] = reader_result["messages"][-1].content
        status_box.write("✅ Scraping complete.")
        render_stage_rail(2, stage_rail_slot)

        status_box.update(label="Running writer chain...")
        status_box.write("✍️ Drafting the structured report...")
        research_combined = (
            f"SEARCH RESULTS : \n {state['search_results']} \n\n"
            f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
        status_box.write("✅ Report drafted.")
        render_stage_rail(3, stage_rail_slot)

        status_box.update(label="Running critic chain...")
        status_box.write("🧐 Critic is reviewing the report...")
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        status_box.write("✅ Review complete.")
        render_stage_rail(4, stage_rail_slot)

        status_box.update(label="Pipeline complete", state="complete")
        return state, None

    except Exception as e:
        status_box.update(label="Pipeline failed", state="error")
        return None, str(e)


# =============================================================================
# SIDEBAR — navigation, input, actions
# =============================================================================
with st.sidebar:
    st.markdown(
        '<div class="eyebrow" style="font-family:\'JetBrains Mono\',monospace;'
        'font-size:0.7rem;letter-spacing:0.14em;color:#E8A33D;text-transform:uppercase;">'
        "RESEARCH DESK</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h2 style="font-family:Fraunces,serif;margin:4px 0 18px 0;font-size:1.4rem;">'
        "Multi-Agent Pipeline</h2>",
        unsafe_allow_html=True,
    )

    st.markdown("**New research run**")
    with st.form("research_form"):
        topic_input = st.text_input(
            "Topic",
            placeholder="e.g. Impact of quantum computing on cryptography",
            label_visibility="collapsed",
        )
        run_clicked = st.form_submit_button("▶ Run research", use_container_width=True)

    st.divider()

    st.markdown("**Session history**")
    if st.session_state.history:
        for i, past_topic in enumerate(reversed(st.session_state.history[-8:])):
            st.markdown(
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.78rem;'
                f'color:#9098A8;padding:4px 0;">· {past_topic}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("No runs yet this session.")

    st.divider()
    if st.button("Clear results", use_container_width=True):
        st.session_state.state = None
        st.session_state.topic = ""
        st.rerun()

    st.caption("Search agent → Reader agent → Writer chain → Critic chain")


# =============================================================================
# MAIN AREA — masthead
# =============================================================================
st.markdown(
    """
    <div class="masthead">
        <div class="eyebrow">Autonomous Research Desk</div>
        <h1>The Multi-Agent Research Pipeline</h1>
        <div class="tagline">Search agent → Reader agent → Writer chain → Critic chain</div>
    </div>
    <br>
    """,
    unsafe_allow_html=True,
)

# Overview cards row
c1, c2, c3, c4 = st.columns(4)
c1.markdown(card("Agents", "4", "amber"), unsafe_allow_html=True)
c2.markdown(card("LLM Backend", "Mistral"), unsafe_allow_html=True)
c3.markdown(card("Search Provider", "Tavily"), unsafe_allow_html=True)
status_label = "Idle" if st.session_state.state is None else "Complete"
status_accent = "" if st.session_state.state is None else "teal"
c4.markdown(card("Pipeline Status", status_label, status_accent), unsafe_allow_html=True)

st.write("")

# =============================================================================
# RUN PIPELINE ON SUBMIT
# =============================================================================
if run_clicked:
    if not topic_input.strip():
        st.warning("Please enter a topic first.")
    else:
        st.session_state.topic = topic_input
        result_state, error = run_pipeline_with_ui(topic_input)
        if error:
            st.error(f"Something went wrong while running the pipeline: {error}")
        else:
            st.session_state.state = result_state
            if topic_input not in st.session_state.history:
                st.session_state.history.append(topic_input)

# =============================================================================
# RESULTS
# =============================================================================
if st.session_state.state:
    state = st.session_state.state
    st.divider()
    st.markdown(
        f'<div class="eyebrow" style="font-family:\'JetBrains Mono\',monospace;'
        f'font-size:0.7rem;letter-spacing:0.14em;color:#E8A33D;text-transform:uppercase;">'
        f"RESULTS</div>"
        f'<h2 style="font-family:Fraunces,serif;margin:4px 0 18px 0;">{st.session_state.topic}</h2>',
        unsafe_allow_html=True,
    )

    tab_report, tab_critic, tab_research = st.tabs(["📄 Report", "🧐 Critic", "🗂️ Raw Research"])

    with tab_report:
        st.markdown(
            f'<div class="content-card">{linkify(state.get("report", "No report generated."))}</div>',
            unsafe_allow_html=True,
        )
        st.write("")
        dl_col, _ = st.columns([1, 3])
        with dl_col:
            st.download_button(
                "↓ Download report (.md)",
                data=state.get("report", ""),
                file_name=f"{st.session_state.topic.replace(' ', '_')}_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

    with tab_critic:
        st.markdown(
            f'<div class="content-card">{linkify(state.get("feedback", "No feedback generated."))}</div>',
            unsafe_allow_html=True,
        )

    with tab_research:
        col_a, col_b = st.columns(2)
        with col_a:
            with st.expander("🔎 Search results", expanded=True):
                st.markdown(f'<div class="raw-block">{state.get("search_results", "")}</div>', unsafe_allow_html=True)
        with col_b:
            with st.expander("📖 Scraped content", expanded=True):
                st.markdown(f'<div class="raw-block">{state.get("scraped_content", "")}</div>', unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="content-card" style="color:#9098A8; font-family:\'JetBrains Mono\',monospace; font-size:0.85rem;">'
        "Enter a topic in the sidebar and run the pipeline to see results here."
        "</div>",
        unsafe_allow_html=True,
    )
