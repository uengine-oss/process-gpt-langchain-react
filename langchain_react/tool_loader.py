from typing import List

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.tools import tool

from .image_generator import generate_single_image, generate_comic


@tool
def create_image(prompt: str, filename: str = None, size: str = "1024x1024", quality: str = "standard") -> str:
    """
    Create an image using OpenAI DALL-E based on a text prompt.
    """
    try:
        return generate_single_image(prompt, filename, size, quality)
    except Exception as e:
        return f"Error generating image: {str(e)}"


@tool
def create_comic(topic: str) -> str:
    """
    Create a 4-panel comic based on a topic using OpenAI DALL-E.
    """
    try:
        return generate_comic(topic)
    except Exception as e:
        return f"Error generating comic: {str(e)}"


async def load_all_tools(session) -> List:
    """Load both MCP tools and image generation tools."""
    mcp_tools = await load_mcp_tools(session)
    image_tools = [create_image, create_comic]
    return mcp_tools + image_tools


