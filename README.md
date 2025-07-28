# LangChain Anchor Browser Integration

A LangChain integration for Anchor Browser, providing tools to interact with web pages programmatically through AI-driven automation.

## Features

- **Content Extraction**: Extract text content from web pages
- **Screenshot Capture**: Take screenshots of web pages
- **AI Web Tasks**: Perform intelligent web tasks using AI (Simple, Standard, Advanced modes)
- **Toolkit Support**: Use all tools together in LangChain workflows
- **Singleton Client**: Efficient API key management and client sharing

## Installation

```bash
# Install from source
git clone <repository-url>
cd langchain-anchorbrowser
pip install -e .

# Or install dependencies manually
pip install langchain anchorbrowser pydantic langchain-openai
```

## Quick Start

### 1. Set up your API key

You can set your API key in advance, or you'll be prompted for it when you first run a tool.
```bash
export ANCHORBROWSER_API_KEY="your_api_key_here"
```

### 2. Running tutorial-demo.py

```bash
python3 scripts/tutorial-demo.py
```

## Configuration

### API Key Management

The integration supports multiple ways to provide your API key:

1. **Environment Variable** (Recommended):
   ```bash
   export ANCHORBROWSER_API_KEY="your_api_key"
   ```

2. **Interactive Prompt**:
   ```python
   # Will prompt for API key if not set in environment
   tool = AnchorContentTool()
   ```

### Singleton Pattern

All tools share the same AnchorClient instance for efficient resource usage.

## Testing

See tests/README.md


