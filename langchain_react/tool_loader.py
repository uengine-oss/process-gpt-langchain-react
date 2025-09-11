from typing import List

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.tools import tool
from .image_generator import ImageGenerator


@tool
def create_image(prompt: str, filename: str = None, size: str = "1024x1024", quality: str = "standard") -> str:
    """
    Create an image using OpenAI GPT Image based on a text prompt.
    Returns a public URL string or an error message.
    """
    try:
        quality_map = {
            "standard": "medium",
            "medium": "medium",
            "low": "low",
            "high": "high",
            "auto": "auto",
        }
        generator = ImageGenerator()
        return generator.generate_and_upload(
            prompt=prompt,
            filename=filename,
            size=size,
            quality=quality_map.get(quality, "medium"),
            resize_to_512=True,
            return_markdown=False,
        )
    except Exception as e:
        return f"Error generating image: {str(e)}"


@tool
def create_comic(topic: str) -> str:
    """
    Create a 4-panel comic (four images) based on a topic using GPT Image.
    Returns a markdown string with four image links.
    """
    try:
        generator = ImageGenerator()
        panel_prompts = [
            f"Four-panel comic, panel 1: A scene about {topic}. Consistent characters, bright colors, minimal text.",
            f"Four-panel comic, panel 2: Progression of the story about {topic}. Same style and characters.",
            f"Four-panel comic, panel 3: A twist or development related to {topic}. Maintain consistency.",
            f"Four-panel comic, panel 4: Punchline or conclusion about {topic}. Cohesive with prior panels.",
        ]

        safe_topic = "".join(ch if ch.isalnum() else "_" for ch in topic)[:40].strip("_") or "topic"
        markdown_images = []
        for idx, p in enumerate(panel_prompts, start=1):
            filename = f"comic_{safe_topic}_{idx}.png"
            md = generator.generate_and_upload(
                prompt=p,
                filename=filename,
                size="1024x1024",
                quality="medium",
                resize_to_512=True,
                return_markdown=True,
            )
            markdown_images.append(md)

        return "\n".join(markdown_images)
    except Exception as e:
        return f"Error generating comic: {str(e)}"


async def load_all_tools(session) -> List:
    """Load both MCP tools and image generation tools."""
    mcp_tools = await load_mcp_tools(session)
    image_tools = [create_image, create_comic]
    return mcp_tools + image_tools


