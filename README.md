# Home Decor Expert

A multi-agent AI system for masculine home decor advice. Marcus (Claude CLI) serves as an autonomous interior design advisor, and a research agent (Gemini CLI) handles live web trend analysis — all running through local CLIs with no API keys required.

## Architecture

```
User ──► Streamlit UI ──► Marcus (Claude CLI)
                              │
                              ▼ (when trends needed)
                         Gemini CLI ──► Web Search
                              │
                              ▼
                         Trend Report ──► back to Marcus
```

| Agent | Engine | Role |
|-------|--------|------|
| **Marcus** | `claude -p` (headless) | Conversational decor advisor — furniture, color palettes, layouts, budgets |
| **Research Agent** | `gemini -p` (headless) | Web trend research, product discovery, market reports |

Marcus decides autonomously when he needs live data. He signals `[RESEARCH: topic]`, the system calls Gemini CLI, then feeds the results back to Marcus for a final answer.

## Prerequisites

- [Claude Code CLI](https://claude.ai/code) — authenticated (`claude` command available)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) — authenticated (`gemini` command available)
- Python 3.10+

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

## Usage

**Chat with Marcus** — ask about room design, furniture picks, color schemes, lighting, or budget breakdowns. He'll ask clarifying questions before recommending.

**Generate Trend Report** — click the sidebar button to run the Gemini research agent independently. Reports are saved to `data/trends/` as markdown files and injected into Marcus's context.

**Automatic research** — when you ask Marcus about trending products or current styles, he'll call Gemini CLI on his own and incorporate the findings.

## Project Structure

```
home-decor-expert/
├── app.py                      # Streamlit UI
├── agents/
│   ├── marcus.py               # Marcus agent (Claude CLI)
│   └── gemini_research.py      # Research agent (Gemini CLI)
├── data/trends/                # Saved trend reports
└── requirements.txt
```
