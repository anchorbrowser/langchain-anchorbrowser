"""
Anchor Browser tools on their own and inside a LangChain 1.x agent.

Requirements:
    pip install langchain-anchorbrowser langchain langchain-openai

Environment variables:
    ANCHORBROWSER_API_KEY  - your Anchor Browser API key
    OPENAI_API_KEY         - your OpenAI API key (only needed for the agent part)
"""

import base64
import importlib.util
import os
import sys

from langchain_anchorbrowser import AnchorContentTool, AnchorScreenshotTool, SimpleAnchorWebTaskTool


def demo_direct_tools():
    print("=== Direct tool usage ===\n")

    html = AnchorContentTool().invoke({"url": "https://example.com"})
    print(f"Fetched {len(html)} characters of HTML. First 200:")
    print(html[:200])
    print()

    encoded = AnchorScreenshotTool().invoke({"url": "https://example.com", "width": 1280, "height": 720})
    image = base64.b64decode(encoded)
    extension = "png" if image.startswith(b"\x89PNG") else "jpg"
    path = f"example-screenshot.{extension}"
    with open(path, "wb") as f:
        f.write(image)
    print(f"Saved screenshot to {path} ({len(image)} bytes)\n")


def demo_agent():
    print("=== Agent with create_agent ===\n")

    if not (importlib.util.find_spec("langchain") and importlib.util.find_spec("langchain_openai")):
        print("Install langchain and langchain-openai to run the agent example:")
        print("  pip install langchain langchain-openai")
        return

    if not os.environ.get("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY to run the agent example.")
        return

    from langchain.agents import create_agent

    # The screenshot tool is left out: its base64 output is meant for code, not for a text model's context.
    agent = create_agent(
        "openai:gpt-4o-mini",
        tools=[AnchorContentTool(), SimpleAnchorWebTaskTool()],
        system_prompt=(
            "You browse the web with Anchor Browser. Use anchor_content_tool to read a page's HTML "
            "and simple_anchor_web_task_tool for anything that needs clicking or navigation."
        ),
    )

    result = agent.invoke({
        "messages": [{"role": "user", "content": "What is the main heading on https://example.com?"}]
    })
    print("Agent response:", result["messages"][-1].content)


if __name__ == "__main__":
    if not os.environ.get("ANCHORBROWSER_API_KEY"):
        print("Set ANCHORBROWSER_API_KEY before running this example.")
        sys.exit(1)

    demo_direct_tools()
    demo_agent()
