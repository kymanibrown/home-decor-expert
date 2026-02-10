"""Marcus Agent — autonomous male home decor expert with tool use.
Marcus runs on Claude. When he needs trend data, he delegates to Gemini CLI."""

import anthropic

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

You have access to a tool called `research_trends` that lets you look up current market trends \
and popular products. Use it when users ask about what's trending, popular products, or when you \
want to back up your recommendations with current market data. Don't use it for every message — \
only when live trend data would genuinely improve your answer.

Always tailor advice to the user's specific situation. If they haven't shared details about their \
space, ask before recommending."""

TOOLS = [
    {
        "name": "research_trends",
        "description": "Search the web for current home decor trends, popular products, and market "
        "data related to a specific topic. Use this when the user asks about what's trending or "
        "when current market data would improve your recommendation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The specific decor topic to research (e.g., 'leather sofas', "
                    "'home office lighting', 'wall art for men')",
                }
            },
            "required": ["topic"],
        },
    }
]


def chat(client: anthropic.Anthropic, messages: list[dict]) -> str:
    """Run Marcus agent with tool use. Research tool calls are handled by Gemini CLI."""
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )

    # Handle tool use loop
    while response.stop_reason == "tool_use":
        tool_results = []
        assistant_content = response.content

        for block in response.content:
            if block.type == "tool_use" and block.name == "research_trends":
                # Delegate research to Gemini CLI in headless mode
                result = run_gemini_research(block.input["topic"])
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        messages = messages + [
            {"role": "assistant", "content": assistant_content},
            {"role": "user", "content": tool_results},
        ]

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

    # Extract the text response
    for block in response.content:
        if hasattr(block, "text"):
            return block.text

    return "I'm having trouble responding right now. Try again."
