# Tests

Unit and integration tests for langchain-anchorbrowser. They mock the Anchor API and need no API key.

## Run Tests

```bash
pip install -e . pytest langchain langchain-tests

pytest tests/                                    # All tests
pytest tests/test_anchor_tools_unit.py           # Content, screenshot and web task tools
pytest tests/test_anchor_task_tools.py           # Task management tools
pytest tests/test_sdk_http.py                    # Tools through the real SDK against mocked HTTP responses
pytest tests/test_agent.py                       # Tools inside a LangChain create_agent graph
pytest tests/test_standard.py                    # LangChain standard tool tests
pytest tests/test_anchor_tools_integration.py    # Client setup, plus live smoke tests
```

The live smoke tests in `test_anchor_tools_integration.py` run only when `ANCHORBROWSER_API_KEY` is set. They call the real API and create and delete browser sessions.
