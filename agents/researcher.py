"""Market Trends Research Agent — powered by Google Gemini.
Searches the web for home decor trends and generates reports."""

import os
from datetime import datetime

from google import genai
from google.genai import types
from duckduckgo_search import DDGS

SYSTEM_PROMPT = """You are a market research analyst specializing in men's home decor and interior design trends. \
Your job is to analyze search results and synthesize actionable trend insights.

When given search results, you:
- Identify the top emerging trends in masculine home decor
- Note specific products, materials, colors, and styles gaining popularity
- Highlight price points and budget tiers when available
- Call out regional or seasonal differences
- Provide confidence levels for each trend (strong, moderate, emerging)

Format your analysis as structured, scannable content with clear sections."""

SEARCH_QUERIES = [
    "men's home decor trends 2025 2026",
    "masculine interior design trending",
    "bachelor pad decor ideas popular",
    "men's apartment design trends",
    "modern masculine living room trends",
    "home office design men 2025 2026",
]


def _get_gemini_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def web_search(query: str, max_results: int = 8) -> list[dict]:
    """Search the web using DuckDuckGo and return results."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return results


def _ask_gemini(gemini_client: genai.Client, prompt: str, max_tokens: int = 2048) -> str:
    """Send a prompt to Gemini and return the text response."""
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text


def research_trends(gemini_api_key: str) -> str:
    """Run a full trend research cycle: search the web, analyze with Gemini, return report."""
    client = _get_gemini_client(gemini_api_key)
    all_results = []
    for query in SEARCH_QUERIES:
        try:
            results = web_search(query, max_results=5)
            all_results.extend(results)
        except Exception:
            continue

    if not all_results:
        return "Unable to fetch trend data at this time."

    search_context = "\n\n".join(
        f"**{r.get('title', 'No title')}**\n{r.get('body', '')}\nSource: {r.get('href', '')}"
        for r in all_results
    )

    return _ask_gemini(
        client,
        f"Analyze these search results and produce a comprehensive trend report "
        f"on current men's home decor trends:\n\n{search_context}",
        max_tokens=2048,
    )


def research_topic(gemini_api_key: str, topic: str) -> str:
    """Research a specific home decor topic on demand."""
    client = _get_gemini_client(gemini_api_key)
    try:
        results = web_search(f"men's home decor {topic} trends ideas", max_results=8)
    except Exception:
        results = []

    if not results:
        return _ask_gemini(
            client,
            f"Based on your knowledge, what are the current trends and best "
            f"recommendations for men's home decor regarding: {topic}",
            max_tokens=1024,
        )

    search_context = "\n\n".join(
        f"**{r.get('title', 'No title')}**\n{r.get('body', '')}\nSource: {r.get('href', '')}"
        for r in results
    )

    return _ask_gemini(
        client,
        f"Analyze these search results about '{topic}' and provide trend "
        f"insights for men's home decor:\n\n{search_context}",
        max_tokens=1024,
    )


def save_report(report: str) -> str:
    """Save a trend report to disk and return the file path."""
    os.makedirs("data/trends", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = f"data/trends/trend_report_{timestamp}.md"
    with open(path, "w") as f:
        f.write(f"# Home Decor Trend Report — {datetime.now().strftime('%B %d, %Y')}\n\n")
        f.write(report)
    return path
