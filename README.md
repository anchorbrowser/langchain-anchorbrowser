# LangChain Anchor Browser Integration

A LangChain integration for [Anchor Browser](https://anchorbrowser.io), providing tools to interact with web pages programmatically through AI-driven automation.

Requires **langchain-core ≥ 1.0** and **anchorbrowser ≥ 1.0**.

## Features

- **Content Extraction** – fetch the markdown text of any URL
- **Screenshot Capture** – take a screenshot of any URL
- **AI Web Tasks** – perform intelligent web tasks using the Anchor AI agent (simple, standard, and advanced modes)
- **Task Management** – create, deploy, run, and inspect reusable browser automation tasks

## Installation

```bash
pip install langchain-anchorbrowser
```

For agent examples you will also need an LLM package, e.g.:

```bash
pip install langchain-anchorbrowser langgraph langchain-openai
```

## Quick Start

### 1. Set your API key

```bash
export ANCHORBROWSER_API_KEY="your_api_key_here"
```

No key yet? [Sign up at anchorbrowser.io](https://anchorbrowser.io).

### 2. Direct tool usage

```python
from langchain_anchorbrowser import AnchorContentTool, AnchorScreenshotTool, SimpleAnchorWebTaskTool

# Fetch page content
content = AnchorContentTool().invoke({"url": "https://example.com"})
print(content)

# Take a screenshot (returns binary image data as a string)
screenshot = AnchorScreenshotTool().invoke({
    "url": "https://example.com",
    "width": 1280,
    "height": 720,
})

# Perform an AI-driven web task
result = SimpleAnchorWebTaskTool().invoke({
    "prompt": "What is the main headline on example.com?",
    "url": "https://example.com",
})
print(result)
```

### 3. Using with a LangChain agent

```python
import os
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_anchorbrowser import AnchorContentTool, AnchorScreenshotTool, SimpleAnchorWebTaskTool

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

tools = [
    AnchorContentTool(),
    AnchorScreenshotTool(),
    SimpleAnchorWebTaskTool(),
]

agent = create_react_agent(llm, tools)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Summarise the homepage of example.com"}]
})
print(result["messages"][-1].content)
```

See `examples/agent_example.py` for a complete runnable script.

## Available Tools

| Tool | Description |
|------|-------------|
| `AnchorContentTool` | Fetch the text content of a URL |
| `AnchorScreenshotTool` | Take a screenshot of a URL |
| `SimpleAnchorWebTaskTool` | Run an AI browser task (prompt + start URL) |
| `StandardAnchorWebTaskTool` | Same, with explicit agent/provider/model selection |
| `AdvancedAnchorWebTaskTool` | Same, with a structured output schema |
| `AnchorTaskCreateTool` | Create a reusable automation task |
| `AnchorTaskListTool` | List your tasks |
| `AnchorTaskDeployTool` | Deploy a new version of a task |
| `AnchorTaskRunTool` | Execute a task |
| `AnchorTaskListExecutionsTool` | List past executions of a task |
| `AnchorTaskDeleteTool` | Delete a task |

Toolkit helpers that bundle related tools:

- `AnchorWebTaskToolKit` – Simple + Standard + Advanced web task tools
- `AnchorTaskToolKit` – All task management tools

## Changelog

### 0.3.0 (2026-11-24)

- **Compatibility**: requires `langchain-core >=1.0` and `anchorbrowser >=1.0` (drops the old `<0.4` pin that blocked modern LangChain stacks).
- **SDK migration**: updated all tools to the anchorbrowser 1.0 SDK.
  - Session creation now uses `sessions.create_session()`.
  - Task tools now use `tasks_legacy.*` (create/list/delete/run/deploy).
  - Delete, deploy, and list-executions tools migrated from raw `httpx` calls to SDK methods.
  - `AnchorContentTool` no longer creates a browser session (the `fetch_webpage` endpoint is session-free).
- **Result handling**: `perform_web_task` now returns the structured result dict from `PerformWebTaskSyncResponseData`; async responses return status and workflow ID.
- **Examples**: added `examples/agent_example.py` with a `create_react_agent` (LangGraph) pattern.
- **Tests**: all existing unit tests updated and new tests added for the SDK-method contracts (58 tests pass, 1 live-API test skipped when no key is present).

### 0.2.0

Initial public release.

## Testing

```bash
# unit tests (no API key required)
pip install pytest
pytest tests/test_anchor_tools_unit.py tests/test_anchor_task_tools.py -v

# live smoke test (requires ANCHORBROWSER_API_KEY)
pytest tests/test_anchor_tools_integration.py -v
```
