"""
LangChain agent example using Anchor Browser tools.

Requirements:
    pip install langchain-anchorbrowser langgraph langchain-openai

Environment variables:
    ANCHORBROWSER_API_KEY  - your Anchor Browser API key
    OPENAI_API_KEY         - your OpenAI API key
"""

import os
import sys

# --- direct tool usage (no LLM needed) ---

from langchain_anchorbrowser import AnchorContentTool, AnchorScreenshotTool, SimpleAnchorWebTaskTool

def demo_direct_tools():
    print("=== Direct tool usage ===\n")

    content_tool = AnchorContentTool()
    content = content_tool.invoke({"url": "https://example.com"})
    print("Page content (first 300 chars):")
    print(content[:300])
    print()

    screenshot_tool = AnchorScreenshotTool()
    screenshot = screenshot_tool.invoke({
        "url": "https://example.com",
        "width": 1280,
        "height": 720,
    })
    print(f"Screenshot captured ({len(screenshot)} bytes of image data)\n")


# --- LangChain react agent (requires langgraph + an LLM provider) ---

def demo_agent():
    print("=== Agent with create_react_agent ===\n")

    try:
        from langgraph.prebuilt import create_react_agent
        from langchain.chat_models import init_chat_model
    except ImportError:
        print("Install langgraph and langchain-openai to run the agent example:")
        print("  pip install langgraph langchain-openai")
        return

    if not os.environ.get("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY to run the agent example.")
        return

    llm = init_chat_model("gpt-4o-mini", model_provider="openai")

    tools = [
        AnchorContentTool(),
        AnchorScreenshotTool(),
        SimpleAnchorWebTaskTool(),
    ]

    agent = create_react_agent(llm, tools)

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": "Get the main heading from https://example.com"}
        ]
    })

    last = result["messages"][-1]
    print("Agent response:", getattr(last, "content", str(last)))


if __name__ == "__main__":
    if not os.environ.get("ANCHORBROWSER_API_KEY"):
        print("Set ANCHORBROWSER_API_KEY before running this example.")
        sys.exit(1)

    demo_direct_tools()
    demo_agent()
