"""
Codex Code Intelligence MCP Server

Provides code generation, refactoring, and code review tools to MCP clients
(Claude Desktop, Cursor, etc.) powered by OpenAI Codex / GPT models.
"""

import os
import sys
import logging
from typing import Optional, Literal
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from openai import AsyncOpenAI
from pydantic import Field

# ─── Setup Logging to stderr ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("codex_mcp")

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY is not set. API calls will fail.")

mcp = FastMCP("codex_mcp")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ─── Tool 1: Generate Code ────────────────────────────────────────────────────

@mcp.tool(
    name="codex_generate_code",
    description="Generate clean, production-ready code in any language based on a detailed prompt.",
)
async def codex_generate_code(
    prompt: str = Field(..., description="Description of the function, class, or script to generate."),
    language: str = Field(default="python", description="Target programming language (e.g. 'python', 'typescript', 'go')."),
    model: Literal["gpt-4o", "gpt-4o-mini", "o3-mini"] = Field(
        default="gpt-4o",
        description="Model to use for generation.",
    ),
) -> str:
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY is not set in environment or .env file."

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an expert software engineer. Write clean, idiomatic, well-documented {language} code. "
                        "Return only the code with necessary comments and type annotations."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or "No code generated."
    except Exception as e:
        return f"Error generating code: {type(e).__name__}: {str(e)}"


# ─── Tool 2: Refactor or Review Code ──────────────────────────────────────────

@mcp.tool(
    name="codex_refactor_code",
    description="Refactor code for performance, readability, bug fixes, or security improvements.",
)
async def codex_refactor_code(
    code: str = Field(..., description="The source code snippet to refactor or analyze."),
    instruction: str = Field(..., description="Refactoring goals (e.g. 'optimize runtime', 'add type hints', 'fix edge cases')."),
    language: Optional[str] = Field(default="python", description="Programming language of the code."),
) -> str:
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY is not set in environment or .env file."

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an expert code reviewer and refactoring specialist for {language}. "
                        "Provide the refactored code followed by a bulleted explanation of improvements."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Instruction: {instruction}\n\nOriginal Code:\n```{language}\n{code}\n```",
                },
            ],
        )
        return response.choices[0].message.content or "No output returned."
    except Exception as e:
        return f"Error refactoring code: {type(e).__name__}: {str(e)}"


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()