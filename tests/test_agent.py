"""Run the Anchor tools inside a LangChain 1.x create_agent graph with a scripted model."""

import unittest

import httpx
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage

try:
    from langchain.agents import create_agent
except ImportError:
    create_agent = None

from langchain_anchorbrowser import AnchorContentTool, SimpleAnchorWebTaskTool
from tests.test_sdk_http import SDKTestCase


class ScriptedToolCallingModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


@unittest.skipIf(create_agent is None, "langchain is not installed")
class TestCreateAgent(SDKTestCase):
    def test_agent_calls_anchor_content_tool(self):
        html = "<html><body><h1>Example Domain</h1></body></html>"
        self.api.route("POST", "/v1/tools/fetch/webpage", lambda r: httpx.Response(
            200, text=html, headers={"content-type": "text/html"}))
        model = ScriptedToolCallingModel(messages=iter([
            AIMessage(content="", tool_calls=[
                {"name": "anchor_content_tool", "args": {"url": "https://example.com"}, "id": "call-1"},
            ]),
            AIMessage(content="The heading is Example Domain."),
        ]))

        agent = create_agent(model, tools=[AnchorContentTool(), SimpleAnchorWebTaskTool()])
        result = agent.invoke({"messages": [{"role": "user", "content": "What is the heading on example.com?"}]})

        tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
        self.assertEqual(len(tool_messages), 1)
        self.assertEqual(tool_messages[0].content, html)
        self.assertEqual(result["messages"][-1].content, "The heading is Example Domain.")


if __name__ == '__main__':
    unittest.main()
