import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_anchorbrowser.AnchorContentTool import AnchorContentTool
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

    def test_real_anchor_browser_connection(self):
        """Live smoke test against the real Anchor Browser API"""
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

        content_tool = AnchorContentTool()

        api_key_set = bool(os.environ.get('ANCHORBROWSER_API_KEY'))
        if not api_key_set:
            self.skipTest("ANCHORBROWSER_API_KEY not set - skipping live smoke test")

        self.assertIsNotNone(content_tool.client)
        self.assertIsNotNone(content_tool.api_key)

        try:
            result = content_tool._run(url="https://example.com")
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0, "API should return non-empty content")
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "authentication" in error_msg or "unauthorized" in error_msg:
                self.fail(f"Connection/Authentication error: {e}")
            # Rate-limiting or other transient errors are acceptable


if __name__ == '__main__':
    unittest.main()
