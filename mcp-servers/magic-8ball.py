"""
Minimal MCP server: a Magic 8-Ball. Ask it anything.
Baby's first MCP server.

Run: pip install mcp && python magic-8ball.py
"""

import random

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("magic-8ball")

ANSWERS = [
    "Yes, absolutely.",
    "Nope.",
    "Ask again after coffee.",
    "Signs point to yes.",
    "Outlook not great, honestly.",
    "Without a doubt.",
    "Better not tell you now.",
    "My sources say no.",
    "Concentrate and ask again.",
    "It is decidedly so.",
]


@mcp.tool()
def shake(question: str) -> str:
    """Ask the Magic 8-Ball a question. Wisdom guaranteed.*"""
    return f"Q: {question}\n🎱 {random.choice(ANSWERS)}"


if __name__ == "__main__":
    mcp.run()
