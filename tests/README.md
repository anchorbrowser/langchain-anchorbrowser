# Tests

Unit and integration tests for langchain-anchorbrowser.

## Run Tests

```bash
# With unittest
python3 -m unittest tests  # All tests
python3 -m unittest tests.test_anchor_tools_unit  # Unit tests
python3 -m unittest tests.test_anchor_tools_integration  # Integration tests

# With pytest
pytest tests/  # All tests
pytest tests/test_anchor_tools_unit.py  # Unit tests
pytest tests/test_anchor_tools_integration.py  # Integration tests
``` 