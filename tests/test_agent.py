"""Run the Anchor tools inside a LangChain 1.x create_agent graph with a scripted model."""

import json

from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage

from langchain_anchorbrowser import AnchorContentTool, SimpleAnchorWebTaskTool
from tests.fake_anchor_api import AnchorAPITestCase

HTML = "<html><body><h1>Example Domain</h1></body></html>"


class ScriptedToolCallingModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


class TestCreateAgent(AnchorAPITestCase):
    def test_agent_runs_anchor_tools(self):
        self.api.route("POST", "/v1/tools/fetch/webpage", body=HTML.encode(), content_type="text/html")
        self.api.route_json("POST", "/v1/tools/perform-web-task", {"data": {"result": {"forecast": "sunny"}}})
        model = ScriptedToolCallingModel(messages=iter([
            AIMessage(content="", tool_calls=[
                {"name": "anchor_content_tool", "args": {"url": "https://example.com"}, "id": "call-1"},
                {"name": "simple_anchor_web_task_tool", "args": {"prompt": "Weather in Tokyo"}, "id": "call-2"},
            ]),
            AIMessage(content="Example Domain; sunny in Tokyo."),
        ]))

        agent = create_agent(model, tools=[AnchorContentTool(), SimpleAnchorWebTaskTool()])
        result = agent.invoke({"messages": [{"role": "user", "content": "Heading of example.com and Tokyo weather?"}]})

        tool_results = {m.tool_call_id: m.content for m in result["messages"] if isinstance(m, ToolMessage)}
        self.assertEqual(tool_results["call-1"], HTML)
        self.assertEqual(json.loads(tool_results["call-2"]), {"forecast": "sunny"})
        self.assertEqual(self.api.calls("POST", "/v1/tools/perform-web-task")[0].json(),
                         {"prompt": "Weather in Tokyo. Ignore the starting url.", "url": "https://example.com"})
        self.assertSessionOpenedAndClosed()
        self.assertEqual(result["messages"][-1].content, "Example Domain; sunny in Tokyo.")

