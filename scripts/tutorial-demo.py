"""
Tutorial demo for Anchor Browser tools with LangChain 1.x.

Requirements:
    pip install langchain-anchorbrowser langchain langchain-openai

Environment variables:
    ANCHORBROWSER_API_KEY  - your Anchor Browser API key
    OPENAI_API_KEY         - your OpenAI API key (prompted for if missing)
"""

import base64
import getpass
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from langchain.agents import create_agent

from langchain_anchorbrowser import AnchorContentTool, AnchorScreenshotTool, AnchorWebTaskToolKit

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

content_tool = AnchorContentTool()
screenshot_tool = AnchorScreenshotTool()
simple_web_task_tool, standard_web_task_tool, advanced_web_task_tool = AnchorWebTaskToolKit().get_tools()

print("=== Anchor Browser Tools Demo ===\n")

print("Example 1: Direct tool usage")
print("-" * 40)

print("1. Taking a screenshot...")
encoded = screenshot_tool.invoke({"url": "https://www.example.com", "width": 1280, "height": 720})
image = base64.b64decode(encoded)
print(f"Screenshot: {len(image)} bytes of image data")

print("\n2. Getting webpage HTML...")
html = content_tool.invoke({"url": "https://www.example.com"})
print(f"Content result: {html[:100]}...")

print("\n3. Performing web task...")
web_task_result = simple_web_task_tool.invoke({"prompt": "What is the weather in Tokyo?"})
print(f"Web task result: {web_task_result[:500]}")

print("\n" + "=" * 50 + "\n")

print("Example 2: Using the tools from an agent")
print("-" * 40)

# The screenshot tool is left out: its base64 output is meant for code, not for a text model's context.
agent = create_agent(
    "openai:gpt-4o-mini",
    tools=[content_tool, simple_web_task_tool, advanced_web_task_tool],
    system_prompt=(
        "You are a helpful assistant that can interact with web pages using Anchor Browser. Tools:\n"
        "1. anchor_content_tool - get the rendered HTML of a webpage\n"
        "2. simple_anchor_web_task_tool - perform simple web tasks\n"
        "3. advanced_anchor_web_task_tool - perform web tasks with a structured output schema\n"
        "Choose the appropriate tool based on the complexity of the user's request."
    ),
)

test_prompts = [
    "What is the main heading on example.com?",
    "Go to a random website and tell me what the page is about",
]

for i, test_prompt in enumerate(test_prompts, 1):
    print(f"\nTest {i}: {test_prompt}")
    print("-" * 30)
    result = agent.invoke({"messages": [{"role": "user", "content": test_prompt}]})
    output = result["messages"][-1].content
    if len(output) > 500:
        output = output[:500] + "..."
    print(f"Result: {output}")

print("\n" + "=" * 50 + "\n")

print("Example 3: Tool chaining")
print("-" * 40)

print("Chaining: Get content -> Perform task")
html = content_tool.invoke({"url": "https://www.example.com"})
print(f"Fetched content:\n{html[:200]}...")

task_result = simple_web_task_tool.invoke({
    "prompt": f"Based on this HTML: {html[:500]}... summarize what this webpage is about"
})
print(f"Chained result: {task_result[:500]}")

print("\n=== Demo Complete ===")
