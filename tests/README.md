# Tests

The tests run the tools, unmodified, against a local fake of the Anchor API (`fake_anchor_api.py`) and need no API key.

## Run Tests

```bash
pip install -e . pytest langchain

pytest tests/                       # All tests
pytest tests/test_tools.py          # Every tool, checked by the requests it sends and what it returns
pytest tests/test_agent.py          # Tools inside a LangChain create_agent graph
pytest tests/test_live_api.py       # Live smoke tests
```

The live smoke tests run only when `ANCHORBROWSER_API_KEY` is set. They call the real API and create and delete browser sessions.
