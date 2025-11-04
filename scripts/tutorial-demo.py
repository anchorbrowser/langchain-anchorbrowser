"""
LangChain v1.0 compatible tutorial demo for Anchor Browser tools.

This script demonstrates how to use Anchor Browser tools with LangChain v1.0.
Key differences from v0.x:
- Uses create_agent instead of create_openai_functions_agent + AgentExecutor
- Uses system_prompt parameter instead of prompts
- Agent is directly invokable (returns Runnable)
- init_chat_model is from langchain.chat_models
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from langchain_anchorbrowser import AnchorWebTaskToolKit, AnchorScreenshotTool, AnchorContentTool

# LangChain v1.0 imports
try:
    from langchain.agents import create_agent
    from langchain.chat_models import init_chat_model
    LANGCHAIN_V1 = True
except ImportError:
    try:
        # Fallback to v0.x imports for backward compatibility
        from langchain.agents import AgentExecutor, create_openai_functions_agent
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.chat_models import init_chat_model
        LANGCHAIN_V1 = False
    except ImportError:
        raise ImportError(
            "Could not import required LangChain modules. "
            "For LangChain v1.0: pip install langchain langchain-openai langchain-core\n"
            "For LangChain v0.x: pip install langchain langchain-openai"
        )

import getpass

# Set up API key
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

# Initialize LLM
llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# Create the tools
anchor_browser_tools = [AnchorScreenshotTool(), AnchorContentTool()] + AnchorWebTaskToolKit().get_tools()

print("=== Anchor Browser Tools Demo (LangChain v1.0) ===\n")

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
# Handle string or other types
screenshot_str = str(screenshot_result)
print(f"Screenshot result: {screenshot_str[:100]}...")

# Use content tool
print("\n2. Getting webpage content...")
content_result = AnchorContentTool().invoke({
    "url": "https://www.example.com",
    "format": "markdown"
})
# Handle string or other types
content_str = str(content_result)
print(f"Content result: {content_str[:100]}...")

# Use web task tool
print("\n3. Performing web task...")
web_task_result = anchor_browser_tools[2].invoke({
    "prompt": "What is the weather in Tokyo?"
})
# Handle string or other types (Data object, dict, etc.)
if isinstance(web_task_result, str):
    print(f"Web task result: {web_task_result}")
else:
    print(f"Web task result: {str(web_task_result)[:500]}")

print("\n" + "="*50 + "\n")

# Example 2: Using with create_agent (v1.0) or AgentExecutor (v0.x)
print("Example 2: Using with AI Agent")
print("-" * 40)

if LANGCHAIN_V1:
    # LangChain v1.0: Use create_agent with system_prompt
    print("Using LangChain v1.0 create_agent...")
    
    # Define the system prompt (replaces the old prompt template)
    system_prompt = """You are a helpful assistant that can interact with web pages using Anchor Browser. You have multiple tools available:
1. anchor_screenshot_tool - Take screenshots of webpages
2. anchor_content_tool - Get content from webpages
3. simple_anchor_web_task_tool - Perform simple web tasks
4. advanced_anchor_web_task_tool - Perform web tasks with advanced configuration

Choose the appropriate tool based on the complexity of the user's request."""

    # Create the agent (returns a Runnable directly)
    agent = create_agent(
        model=llm,
        tools=anchor_browser_tools,
        system_prompt=system_prompt
    )
    
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
            # Invoke directly (no need for AgentExecutor wrapper)
            # Input format: messages list with HumanMessage or dict
            result = agent.invoke({
                "messages": [{"role": "user", "content": test_prompt}]
            })
            
            # Extract the last message content as output
            # In v1.0, result is typically a dict with "messages" key
            if isinstance(result, dict) and "messages" in result:
                last_message = result["messages"][-1]
                # Handle both message objects and dicts
                if hasattr(last_message, "content"):
                    output = last_message.content
                elif hasattr(last_message, "text"):  # New v1.0 property
                    output = last_message.text
                elif isinstance(last_message, dict):
                    output = last_message.get("content", last_message.get("text", str(result)))
                else:
                    output = str(last_message)
            elif isinstance(result, dict) and "output" in result:
                # Fallback for other response formats
                output = result["output"]
            else:
                output = str(result)
            
            # Truncate long outputs for display
            if isinstance(output, str) and len(output) > 500:
                output = output[:500] + "..."
            print(f"Result: {output}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
else:
    # LangChain v0.x: Use create_openai_functions_agent + AgentExecutor
    print("Using LangChain v0.x AgentExecutor...")
    
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    # Define the prompt template for the AI Agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can interact with web pages using Anchor Browser. You have multiple tools available:\n"
                  "1. anchor_screenshot_tool - Take screenshots of webpages\n"
                  "2. anchor_content_tool - Get content from webpages\n"
                  "3. simple_anchor_web_task_tool - Perform simple web tasks\n"
                  "4. advanced_anchor_web_task_tool - Perform web tasks with advanced configuration\n"
                  "Choose the appropriate tool based on the complexity of the user's request."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create the AI Agent
    agent_runnable = create_openai_functions_agent(llm, anchor_browser_tools, prompt)
    agent_executor = AgentExecutor(agent=agent_runnable, tools=anchor_browser_tools, verbose=True)

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
# Convert content to string for display and use in prompt
content_str = str(content)
print(f"Fetched Content:\n{content_str[:200]}...")  # Limit content display

task_result = anchor_browser_tools[2].invoke({
    "prompt": f"Based on this content: {content_str[:200]}..., summarize what this webpage is about"
})

# Handle different result types (string, Data object, dict, etc.)
if isinstance(task_result, str):
    result_str = task_result[:500] if len(task_result) > 500 else task_result
else:
    result_str = str(task_result)
    if len(result_str) > 500:
        result_str = result_str[:500] + "..."
print(f"Chained result: {result_str}")

print("\n=== Demo Complete ===")

