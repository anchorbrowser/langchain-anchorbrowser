import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

from langchain_anchorbrowser.AnchorWebTaskTool import AnchorWebTaskToolKit
from langchain_anchorbrowser.AnchorScreenshotTool import AnchorScreenshotTool
from langchain_anchorbrowser.AnchorContentTool import AnchorContentTool

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
import getpass

# Set up API key
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

# Initialize LLM
llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# Create the tools
anchor_browser_tools = [AnchorScreenshotTool(), AnchorContentTool()] + AnchorWebTaskToolKit().get_tools()

print("=== Separate Anchor Browser Tools Demo ===\n")

# Example 1: Direct tool usage
print("Example 1: Direct tool usage")
print("-" * 40)

# Use screenshot tool
print("1. Taking a screenshot...")
screenshot_result = AnchorScreenshotTool().invoke({
    "url": "https://www.example.com",
    "width": 1280,
    "height": 720
})
print(f"Screenshot result: {screenshot_result[:100]}...")

# Use content tool
print("\n2. Getting webpage content...")
content_result = AnchorContentTool().invoke({
    "url": "https://www.example.com",
    "format": "markdown"
})
print(f"Content result: {content_result[:100]}...")

# Use web task tool
print("\n3. Performing web task...")
web_task_result = anchor_browser_tools[2].invoke({
    "prompt": "What is the weather in Tokyo?"
})
print(f"Web task result: {web_task_result}")

print("\n" + "="*50 + "\n")

# Example 2: Using with AgentExecutor
print("Example 2: Using with AgentExecutor")
print("-" * 40)
if not os.environ.get("OPENAI_API_KEY"):
    print("OPENAI_API_KEY is not set")
    exit()

# Define the prompt template for the AI Agent
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that can interact with web pages using Anchor Browser. You have multiple tools available:\n"
              "1. anchor_screenshot_tool - Take screenshots of webpages\n"
              "2. anchor_content_tool - Get content from webpages\n"
              "3. simple_anchor_web_task_tool - Perform simple web tasks\n"
              "4. standard_anchor_web_task_tool - Perform web tasks with  standard configuration\n"
              "5. advanced_anchor_web_task_tool - Perform web tasks with full advanced configuration\n"
              "Choose the appropriate tool based on the complexity of the user's request."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the AI Agent
agent = create_openai_functions_agent(llm, anchor_browser_tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=anchor_browser_tools, verbose=True)

# Test different scenarios with the AI Agent
test_prompts = [
    "Take a screenshot of example.com",
    "Get the content of example.com in markdown format",
    "Go to a random website and tell me what the page is about"
]

for i, test_prompt in enumerate(test_prompts, 1):
    print(f"\nTest {i}: {test_prompt}")
    print("-" * 30)
    
    try:
        result = agent_executor.invoke({"input": test_prompt})
        print(f"Result: {result['output']}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Example 3: Tool chaining
print("Example 3: Tool chaining")
print("-" * 40)

# Chain: Get content → Perform task on that content
print("Chaining: Get content → Perform task")
content = anchor_browser_tools[1].invoke({
    "url": "https://www.example.com",
    "format": "markdown"
})
print(f"Fetched Content:\n{content}")
task_result = anchor_browser_tools[2].invoke({
    "prompt": f"Based on this content: {content[:200]}..., summarize what this webpage is about"
})

print(f"Chained result: {task_result}") 