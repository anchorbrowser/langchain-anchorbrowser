# LangChain Anchor Browser Integration

A LangChain integration for [Anchor Browser](https://anchorbrowser.io), providing tools to interact with web pages programmatically through AI-driven automation.

Requires **Python ≥ 3.10**, **langchain-core ≥ 1.0** and **anchorbrowser ≥ 1.0**.

## Features

- **Content Extraction** – fetch the fully rendered HTML of any URL
- **Screenshot Capture** – take a screenshot of any URL, returned as a base64-encoded image
- **AI Web Tasks** – perform intelligent web tasks using the Anchor AI agent (simple, standard, and advanced modes)
- **Task Management** – create, deploy, run, and inspect reusable browser automation tasks

## Installation

```bash
pip install langchain-anchorbrowser
```

To use the tools from a LangChain agent you also need `langchain` and a model provider package, e.g.:

```bash
pip install langchain-anchorbrowser langchain langchain-openai
```

## Quick Start

### 1. Set your API key

```bash
export ANCHORBROWSER_API_KEY="your_api_key_here"
```

No key yet? [Sign up at anchorbrowser.io](https://anchorbrowser.io).

### 2. Direct tool usage

```python
import base64

from langchain_anchorbrowser import AnchorContentTool, AnchorScreenshotTool, SimpleAnchorWebTaskTool

# Fetch the rendered HTML of a page
html = AnchorContentTool().invoke({"url": "https://example.com"})
print(html[:300])

# Take a screenshot (returns the image as a base64 string)
encoded = AnchorScreenshotTool().invoke({
    "url": "https://example.com",
    "width": 1280,
    "height": 720,
})
image = base64.b64decode(encoded)
extension = "png" if image.startswith(b"\x89PNG") else "jpg"
with open(f"screenshot.{extension}", "wb") as f:
    f.write(image)

# Perform an AI-driven web task
result = SimpleAnchorWebTaskTool().invoke({
    "prompt": "What is the main headline on example.com?",
    "url": "https://example.com",
})
print(result)
```

### 3. Using with a LangChain agent

```python
from langchain.agents import create_agent
from langchain_anchorbrowser import AnchorContentTool, SimpleAnchorWebTaskTool

agent = create_agent(
    "openai:gpt-4o-mini",
    tools=[AnchorContentTool(), SimpleAnchorWebTaskTool()],
    system_prompt="You browse the web with Anchor Browser tools.",
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What is the main heading on https://example.com?"}]
})
print(result["messages"][-1].content)
```

The screenshot tool is intended for direct use: its base64 output is large and not useful as text in a model's context.

See `examples/agent_example.py` for a complete runnable script.

## Available Tools

| Tool | Description |
|------|-------------|
| `AnchorContentTool` | Fetch the fully rendered HTML of a URL |
| `AnchorScreenshotTool` | Take a screenshot of a URL (base64-encoded PNG or JPEG) |
| `SimpleAnchorWebTaskTool` | Run an AI browser task (prompt + start URL) |
| `StandardAnchorWebTaskTool` | Same, with explicit agent/provider/model selection |
| `AdvancedAnchorWebTaskTool` | Same, with a structured output schema |
| `AnchorTaskCreateTool` | Create a reusable automation task |
| `AnchorTaskListTool` | List your tasks |
| `AnchorTaskDeployTool` | Deploy a new version of a task |
| `AnchorTaskRunTool` | Execute a task |
| `AnchorTaskListExecutionsTool` | List past executions of a task |
| `AnchorTaskDeleteTool` | Delete a task |

`AnchorContentTool` returns text. Binary downloads such as PDFs are not supported.

The task tools return the API's JSON response body unchanged.

Toolkit helpers that bundle related tools:

- `AnchorWebTaskToolKit` – Simple + Standard + Advanced web task tools
- `AnchorTaskToolKit` – All task management tools

### Browser sessions and logging

The screenshot and web task tools create a browser session for each call and delete it when the call finishes, including when it fails. The content tool does not need a session.

The tools log to the `langchain_anchorbrowser` logger. Only session ids are logged, never connection URLs.

## Changelog

### 0.3.0

- **Compatibility**: requires `langchain-core >=1.0`, `anchorbrowser >=1.0` and Python 3.10+ (drops the old `<0.4` pin that blocked modern LangChain stacks).
  - langchain-core 1.3 and later pass schema defaults to tools; earlier versions do not. Options the API defaults itself (`url` and `output_schema` on the web task tools, `agent` on the standard web task tool, `language` on the deploy tool) now default to unset, so each tool sends the same request on every langchain-core 1.x. A web task without a `url` still starts on example.com with a hint to ignore it.
- **SDK migration**: updated all tools to the anchorbrowser 1.0 SDK.
  - Session creation now uses `sessions.create_session()`.
  - Task tools now use `tasks_legacy.*` (create/list/delete/run/deploy).
  - Delete, deploy, and list-executions tools migrated from raw `httpx` calls to SDK methods.
  - `AnchorContentTool` no longer creates a browser session (the `fetch_webpage` endpoint is session-free).
- **Fixes**
  - `AnchorScreenshotTool` returns the image as a base64 string. It used to decode the image bytes as text, which corrupted them.
  - Browser sessions created by the tools are now deleted after each call. Previously they were left open.
  - The tools no longer log the full session object (which includes the CDP URL) or print the live view URL; only the session id is logged.
  - `AnchorTaskListTool` and `AnchorTaskListExecutionsTool` returned `{}`; they now return the API payload (`tasks`, `total`, `page`, `limit` and `results`, `pagination`).
  - The web task tools return the task result as a JSON string.
  - The task tools return the response body as the API sent it, instead of the SDK model with renamed keys and empty fields.
  - The first tool calls of an agent that runs tools in parallel could fail with `'NoneType' object has no attribute 'sessions'`. The shared client is now created under a lock.
- **Breaking**: `AnchorContentTool` no longer has a `format` option. The API always returned HTML, so the option had no effect; passing it is still accepted and ignored.
- **Examples**: `examples/agent_example.py`, the tutorial script and the notebook use LangChain 1.x `create_agent`.
- **Packaging**: removed the stale `requirements.lock` and `requirements-dev.lock` files and regenerated `poetry.lock`.

### 0.2.0

Initial public release.

## Testing

```bash
pip install -e . pytest langchain
pytest
```

The tests run the tools against a local fake of the Anchor API and need no API key. The live smoke tests in `tests/test_live_api.py` run only when `ANCHORBROWSER_API_KEY` is set.
