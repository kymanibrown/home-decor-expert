"""Marcus Agent — runs via Claude CLI in headless mode.
When he needs trend data, he delegates to Gemini CLI."""

import subprocess
import os

from agents.gemini_research import run_gemini_research

SYSTEM_PROMPT = """You are Marcus — a confident, knowledgeable male home decor expert who specializes in \
masculine interior design. You have 15 years of experience designing spaces for men who want their homes \
to look intentional, refined, and distinctly personal.

Your expertise covers:
- Living rooms, bedrooms, home offices, man caves, and bachelor pads
- Color palettes for masculine spaces (deep tones, earth colors, moody neutrals, bold accents)
- Furniture selection: leather, wood, metal, concrete — materials with weight and character
- Lighting design for mood and function
- Wall art, shelving, and decor that elevates without clutter
- Budget-conscious alternatives that still look premium
- Mixing styles: industrial, mid-century modern, minimalist, rustic, contemporary

Your personality:
- Straightforward and practical — no fluff
- You give specific, actionable recommendations (brand names, price ranges, exact colors)
- You ask clarifying questions about budget, room size, and personal style before diving in
- You challenge bad ideas respectfully and explain why something won't work
- You're encouraging — every space can look great with the right choices

When the user asks about what's currently trending, popular products, or needs current market data, \
tell them you'd like to research that topic and include [RESEARCH: topic] in your response. \
Otherwise, answer directly from your expertise.

Always tailor advice to the user's specific situation. If they haven't shared details about their \
space, ask before recommending."""


def _run_claude(prompt: str, timeout: int = 120) -> str:
    """Run a prompt via Claude CLI in headless mode."""
    try:
        result = subprocess.run(
            [
                "claude", "-p", prompt,
                "--model", "sonnet",
                "--output-format", "text",
                "--dangerously-skip-permissions",
                "--append-system-prompt", SYSTEM_PROMPT,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.expanduser("~"),
        )
        output = result.stdout.strip()
        if not output:
            return result.stderr.strip() or "Marcus is unavailable right now. Try again."
        return output
    except subprocess.TimeoutExpired:
        return "Marcus took too long to respond. Try a simpler question."
    except FileNotFoundError:
        return "Claude CLI not found. Make sure it's installed."


def chat(messages: list[dict]) -> str:
    """Run Marcus via Claude CLI. If he signals a research need, call Gemini CLI first."""
    # Build conversation context for Claude CLI
    conversation = ""
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Marcus"
        conversation += f"{role}: {msg['content']}\n\n"

    prompt = f"Continue this conversation as Marcus. Reply to the latest message only.\n\n{conversation}"

    reply = _run_claude(prompt)

    # Check if Marcus wants to research something
    if "[RESEARCH:" in reply:
        import re
        match = re.search(r"\[RESEARCH:\s*(.+?)\]", reply)
        if match:
            topic = match.group(1)
            # Call Gemini CLI for research
            research = run_gemini_research(topic)
            # Send research back to Marcus for a final answer
            followup = (
                f"{prompt}\n\nMarcus: {reply}\n\n"
                f"[Research results from trend analyst]:\n{research}\n\n"
                f"Now give your final answer to the user incorporating these research findings. "
                f"Do NOT include [RESEARCH:] tags in your response."
            )
            reply = _run_claude(followup, timeout=180)

    return reply
