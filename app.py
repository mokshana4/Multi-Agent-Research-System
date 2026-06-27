import streamlit as st
from pipeline import run_research_pipeline

st.set_page_config(
    page_title="Research Pipeline",
    page_icon="🧬",
    layout="wide",
)

# ----------------------------------------------------------------------------
# THEME
# Palette: midnight slate background, amber accent (the "agent at work" glow),
# teal as a secondary signal color, warm off-white text.
# Display face: a serif for the masthead (gives it a "research journal" feel)
# Body/UI face: a clean grotesk
# Mono: for URLs / raw data
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg: #0F1117;
        --panel: #171a23;
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

    .masthead {
        display: flex;
        align-items: baseline;
        gap: 14px;
        border-bottom: 1px solid var(--panel-border);
        padding-bottom: 18px;
        margin-bottom: 28px;
    }
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
        font-size: 2.4rem;
        margin: 0;
        color: var(--text);
        line-height: 1.05;
    }
    .masthead .tagline {
        font-size: 0.95rem;
        color: var(--text-dim);
        margin-top: 4px;
    }

    .stage-rail {
        display: flex;
        gap: 10px;
        margin: 6px 0 22px 0;
        flex-wrap: wrap;
    }
    .stage-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.74rem;
        padding: 6px 12px;
        border-radius: 999px;
        border: 1px solid var(--panel-border);
        color: var(--text-dim);
        background: var(--panel);
        transition: all 0.25s ease;
    }
    .stage-pill.active {
        border-color: var(--amber);
        color: var(--amber);
        box-shadow: 0 0 0 1px rgba(232,163,61,0.25), 0 0 14px rgba(232,163,61,0.18);
    }
    .stage-pill.done {
        border-color: var(--teal);
        color: var(--teal);
    }

    .stTextInput input {
        background: var(--panel) !important;
        border: 1px solid var(--panel-border) !important;
        color: var(--text) !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
    }
    .stTextInput input:focus {
        border-color: var(--amber) !important;
        box-shadow: 0 0 0 1px var(--amber) !important;
    }
    label, .stTextInput label p {
        color: var(--text-dim) !important;
        font-size: 0.85rem !important;
    }

    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, var(--amber), #c9842a);
        color: #161310;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(232,163,61,0.3);
    }

    div[data-testid="stStatusWidget"], div[data-testid="stExpander"] {
        background: var(--panel) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 12px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid var(--panel-border);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-dim);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        color: var(--amber) !important;
        border-bottom: 2px solid var(--amber) !important;
    }

    .content-card {
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-radius: 14px;
        padding: 28px 32px;
        line-height: 1.65;
    }
    .content-card h1, .content-card h2, .content-card h3 {
        font-family: 'Fraunces', serif;
        color: var(--amber);
    }
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
        background: transparent;
        border: 1px solid var(--teal);
        color: var(--teal);
        border-radius: 10px;
    }
    .stDownloadButton button:hover {
        background: rgba(63,191,168,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# MASTHEAD
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="masthead">
        <div>
            <div class="eyebrow">Autonomous Research Desk</div>
            <h1>The Multi-Agent Research Pipeline</h1>
            <div class="tagline">Search agent → Reader agent → Writer chain → Critic chain</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "state" not in st.session_state:
    st.session_state.state = None
if "topic" not in st.session_state:
    st.session_state.topic = ""

STAGES = ["Search", "Read", "Write", "Critique"]


def render_stage_rail(active_index: int):
    pills = ""
    for i, name in enumerate(STAGES):
        cls = "stage-pill"
        if i < active_index:
            cls += " done"
        elif i == active_index:
            cls += " active"
        pills += f'<div class="{cls}">{i+1:02d} · {name}</div>'
    st.markdown(f'<div class="stage-rail">{pills}</div>', unsafe_allow_html=True)


with st.form("research_form"):
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Impact of quantum computing on cryptography",
    )
    submitted = st.form_submit_button("Run research →", use_container_width=False)

if submitted:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        st.session_state.topic = topic
        stage_slot = st.empty()
        progress_box = st.status("Starting pipeline...", expanded=True)

        try:
            from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

            state = {}

            with stage_slot:
                render_stage_rail(0)
            progress_box.update(label="Running search agent...")
            progress_box.write("🔎 Searching the web for recent, relevant sources...")
            search_agent = build_search_agent()
            search_result = search_agent.invoke(
                {"messages": [("user", f"Find recent, relatable and detailed information about: {topic}")]}
            )
            state["search_results"] = search_result["messages"][-1].content
            progress_box.write("✅ Search complete.")

            with stage_slot:
                render_stage_rail(1)
            progress_box.update(label="Running reader agent...")
            progress_box.write("📖 Scraping the most relevant source for deeper content...")
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
            progress_box.write("✅ Scraping complete.")

            with stage_slot:
                render_stage_rail(2)
            progress_box.update(label="Running writer chain...")
            progress_box.write("✍️ Drafting the structured report...")
            research_combined = (
                f"SEARCH RESULTS : \n {state['search_results']} \n\n"
                f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
            )
            state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
            progress_box.write("✅ Report drafted.")

            with stage_slot:
                render_stage_rail(3)
            progress_box.update(label="Running critic chain...")
            progress_box.write("🧐 Critic is reviewing the report...")
            state["feedback"] = critic_chain.invoke({"report": state["report"]})
            progress_box.write("✅ Review complete.")

            with stage_slot:
                render_stage_rail(4)
            progress_box.update(label="Pipeline complete", state="complete")
            st.session_state.state = state

        except Exception as e:
            progress_box.update(label="Pipeline failed", state="error")
            st.error(f"Something went wrong while running the pipeline: {e}")

# ----------------------------------------------------------------------------
# RESULTS
# ----------------------------------------------------------------------------
if st.session_state.state:
    state = st.session_state.state
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="eyebrow" style="margin-bottom:6px;">RESULTS</div>'
        f'<h2 style="font-family:Fraunces,serif;margin-top:0;">{st.session_state.topic}</h2>',
        unsafe_allow_html=True,
    )

    tab_report, tab_critic, tab_research = st.tabs(["Report", "Critic", "Raw Research"])

    with tab_report:
        st.markdown(f'<div class="content-card">{state.get("report", "No report generated.")}</div>', unsafe_allow_html=True)
        st.write("")
        st.download_button(
            "↓ Download report (.md)",
            data=state.get("report", ""),
            file_name=f"{st.session_state.topic.replace(' ', '_')}_report.md",
            mime="text/markdown",
        )

    with tab_critic:
        feedback = state.get("feedback", "No feedback generated.")
        st.markdown(f'<div class="content-card">{feedback}</div>', unsafe_allow_html=True)

    with tab_research:
        st.markdown('<div class="eyebrow" style="margin:10px 0 6px;">Search Results</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="raw-block">{state.get("search_results", "")}</div>', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow" style="margin:18px 0 6px;">Scraped Content</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="raw-block">{state.get("scraped_content", "")}</div>', unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="content-card" style="color:var(--text-dim); font-family:JetBrains Mono, monospace; font-size:0.85rem;">'
        "Enter a topic above and run the pipeline to see the report here."
        "</div>",
        unsafe_allow_html=True,
    )