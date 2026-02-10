"""Orchestrator for Gemini CLI — runs research tasks in headless mode and captures output."""

import subprocess
import os
from datetime import datetime


def run_gemini_research(topic: str, timeout: int = 120) -> str:
    """Run a research task via Gemini CLI in headless mode (-p flag).
    Returns the text output from Gemini."""
    prompt = (
        f"You are a market research analyst specializing in men's home decor. "
        f"Search the web for current trends related to: '{topic}'. "
        f"Find specific products, brands, price ranges, trending styles, and materials. "
        f"Provide a structured analysis with sections for: "
        f"Top Trends, Recommended Products, Price Ranges, and Style Notes. "
        f"Be specific and actionable — include real brand names and prices."
    )

    try:
        result = subprocess.run(
            ["gemini", "-p", prompt, "-o", "text", "--yolo"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.expanduser("~"),
        )
        output = result.stdout.strip()
        if not output:
            return result.stderr.strip() or "Gemini CLI returned no output."
        return output
    except subprocess.TimeoutExpired:
        return f"Gemini CLI timed out after {timeout}s researching '{topic}'."
    except FileNotFoundError:
        return "Gemini CLI not found. Install it or check your PATH."


def run_gemini_trend_report(timeout: int = 180) -> str:
    """Generate a full trend report via Gemini CLI."""
    prompt = (
        "You are a market research analyst specializing in men's home decor and interior design. "
        "Search the web for the latest trends in masculine home decor for 2025-2026. "
        "Cover these areas:\n"
        "1. Living room and lounge trends\n"
        "2. Home office design for men\n"
        "3. Bedroom and bachelor pad trends\n"
        "4. Popular materials and color palettes\n"
        "5. Trending furniture brands and products with price ranges\n"
        "6. Emerging styles (industrial, mid-century modern, minimalist, etc.)\n\n"
        "For each area, rate the trend strength (strong/moderate/emerging) "
        "and include specific product recommendations with prices. "
        "Format as a clean, structured report with markdown headers."
    )

    try:
        result = subprocess.run(
            ["gemini", "-p", prompt, "-o", "text", "--yolo"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.expanduser("~"),
        )
        output = result.stdout.strip()
        if not output:
            return result.stderr.strip() or "Gemini CLI returned no output."
        return output
    except subprocess.TimeoutExpired:
        return f"Gemini CLI timed out after {timeout}s generating trend report."
    except FileNotFoundError:
        return "Gemini CLI not found. Install it or check your PATH."


def save_report(report: str) -> str:
    """Save a trend report to disk and return the file path."""
    os.makedirs("data/trends", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = f"data/trends/trend_report_{timestamp}.md"
    with open(path, "w") as f:
        f.write(f"# Home Decor Trend Report — {datetime.now().strftime('%B %d, %Y')}\n\n")
        f.write(report)
    return path
