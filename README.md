# Multi-Agent AI Research System
A multi-agent AI research system built with LangChain and Streamlit. Four specialized agents — Search, Reader, Writer, and Critic — work in sequence to automatically research any topic, scrape relevant sources, draft a report, and review it for quality.

## How It Works
The pipeline runs 4 agents in sequence:
1. *Search Agent* — Queries the web for recent and reliable information on the topic
2. *Reader Agent* — Picks the most relevant URL and scrapes it for deeper content
3. *Writer Chain* — Drafts a structured research report from all gathered data
4. *Critic Chain* — Reviews the report and provides quality feedback

The Streamlit UI runs the topic input and controls from a sidebar, with live stage tracking (Search → Read → Write → Critique) and tabbed output for the Report, Critic feedback, and Raw Research.

## Features
- Live stage tracking as each agent runs
- Session history of past research topics
- Tabbed results: final report, critic review, and raw research
- One-click report download as Markdown

## Tech Stack
- Python
- LangChain
- Streamlit
- Mistral AI (LLM)
- Tavily (Web Search)
- BeautifulSoup (Web Scraping)

## Setup & Installation
1. Clone the repository
```bash
git clone https://github.com/mokshana4/Multi-Agent-Research-System.git
cd Multi-Agent-Research-System
```
2. Create and activate virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Add your API keys in a `.env` file
MISTRAL_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
5. Run the app
```bash
streamlit run app.py
```
## Live Demo
[View the deployed app](https://multi-agent-research-system-dg8gcziu49cxeahbfhrgzs.streamlit.app)

## Author
Made by [mokshana4](https://github.com/mokshana4)
