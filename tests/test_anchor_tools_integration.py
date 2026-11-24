import base64
import json
import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_anchorbrowser.AnchorContentTool import AnchorContentTool
from langchain_anchorbrowser.AnchorTaskListTool import AnchorTaskListTool
from langchain_anchorbrowser.AnchorScreenshotTool import AnchorScreenshotTool
from langchain_anchorbrowser.AnchorWebTaskTool import (
    SimpleAnchorWebTaskTool,
    StandardAnchorWebTaskTool,
    AdvancedAnchorWebTaskTool,
    AnchorWebTaskToolKit
)
from langchain_anchorbrowser.AnchorBaseTool import AnchorClient


class TestAnchorToolsIntegration(unittest.TestCase):
    """Integration tests for Anchor Browser tools"""

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    @patch.dict(os.environ, {'ANCHORBROWSER_API_KEY': 'test_key'})
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    def test_singleton_client_shared_across_tools(self, mock_anchorbrowser):
        """Test that all tools share the same AnchorClient singleton instance"""
        mock_anchorbrowser.return_value = Mock()

        content_tool = AnchorContentTool()
        screenshot_tool = AnchorScreenshotTool()
        web_task_tool = SimpleAnchorWebTaskTool()

        self.assertIs(content_tool.client, screenshot_tool.client)
        self.assertIs(screenshot_tool.client, web_task_tool.client)
        self.assertIs(content_tool.api_key, screenshot_tool.api_key)
        self.assertIs(screenshot_tool.api_key, web_task_tool.api_key)

        client1 = AnchorClient()
        client2 = AnchorClient()
        self.assertIs(client1, client2)

    @patch.dict(os.environ, {'ANCHORBROWSER_API_KEY': 'test_key'})
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    def test_web_task_toolkit_integration_with_all_tools(self, mock_anchorbrowser):
        """Test that the web task toolkit properly integrates all web task tools"""
        mock_anchorbrowser.return_value = Mock()

        web_task_toolkit = AnchorWebTaskToolKit()
        web_task_tools = web_task_toolkit.get_tools()

        self.assertEqual(len(web_task_tools), 3)

        tool_names = [tool.name for tool in web_task_tools]
        expected_names = [
            "simple_anchor_web_task_tool",
            "standard_anchor_web_task_tool",
            "advanced_anchor_web_task_tool"
        ]
        self.assertEqual(tool_names, expected_names)

        clients = [tool.client for tool in web_task_tools]
        self.assertTrue(all(client is clients[0] for client in clients))

        api_keys = [tool.api_key for tool in web_task_tools]
        self.assertTrue(all(api_key is api_keys[0] for api_key in api_keys))

    @patch.dict(os.environ, {'ANCHORBROWSER_API_KEY': 'test_env_key'})
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    def test_environment_variable_integration(self, mock_anchorbrowser):
        """Test integration with environment variables for API key"""
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

        mock_client = Mock()
        mock_tools = Mock()
        mock_client.tools = mock_tools
        mock_anchorbrowser.return_value = mock_client

        mock_tools.fetch_webpage = Mock(return_value="# Example")

        tool = AnchorContentTool()
        tool.invoke({"url": "https://example.com"})

        mock_anchorbrowser.assert_called_once_with(api_key='test_env_key')

    def test_content_tool_needs_no_session(self):
        """AnchorContentTool.needs_session should be False"""
        tool = AnchorContentTool()
        self.assertFalse(tool.needs_session)

    def test_screenshot_tool_needs_session(self):
        """AnchorScreenshotTool.needs_session should be True (default)"""
        tool = AnchorScreenshotTool()
        self.assertTrue(tool.needs_session)

    def test_web_task_tools_need_session(self):
        """Web task tools should need a session by default"""
        for cls in (SimpleAnchorWebTaskTool, StandardAnchorWebTaskTool, AdvancedAnchorWebTaskTool):
            self.assertTrue(cls().needs_session, f"{cls.__name__} should need a session")

@unittest.skipUnless(os.environ.get("ANCHORBROWSER_API_KEY"), "ANCHORBROWSER_API_KEY not set")
class TestLiveAnchorAPI(unittest.TestCase):
    """Live smoke tests against the real Anchor Browser API. Any error fails the test."""

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    def invoke_and_check_session_closed(self, tool, tool_input):
        sessions = tool.client.sessions
        with patch.object(sessions, "delete_session", wraps=sessions.delete_session) as delete_session, \
                self.assertNoLogs("langchain_anchorbrowser", level="WARNING"):
            result = tool.invoke(tool_input)
        delete_session.assert_called_once()
        return result

    def test_content_returns_html(self):
        html = AnchorContentTool().invoke({"url": "https://example.com"})

        self.assertIsInstance(html, str)
        self.assertIn("Example Domain", html)

    def test_screenshot_returns_base64_image(self):
        encoded = self.invoke_and_check_session_closed(
            AnchorScreenshotTool(), {"url": "https://example.com", "width": 800, "height": 600})

        image = base64.b64decode(encoded, validate=True)
        self.assertGreater(len(image), 1000)
        self.assertTrue(image.startswith((b"\xff\xd8\xff", b"\x89PNG")), "expected JPEG or PNG bytes")

    def test_web_task_returns_result(self):
        result = self.invoke_and_check_session_closed(
            SimpleAnchorWebTaskTool(),
            {"prompt": "What is the main heading on this page? Reply with the heading text.", "url": "https://example.com"},
        )

        payload = json.loads(result)
        self.assertTrue(payload)
        self.assertIn("example domain", json.dumps(payload).lower())

    def test_list_tasks_returns_payload(self):
        payload = json.loads(AnchorTaskListTool().invoke({"page": "1", "limit": "5"}))

        self.assertIn("tasks", payload)
        self.assertIsInstance(payload["tasks"], list)
        self.assertIn("total", payload)


if __name__ == '__main__':
    unittest.main()
