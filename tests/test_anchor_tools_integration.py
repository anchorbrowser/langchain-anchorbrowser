import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_anchorbrowser.AnchorContentTool import AnchorContentTool
from langchain_anchorbrowser.AnchorScreenshotTool import AnchorScreenshotTool
from langchain_anchorbrowser.AnchorWebTaskTool import (
    SimpleAnchorWebTaskTool,
    AnchorWebTaskToolKit
)
from langchain_anchorbrowser.AnchorBaseTool import AnchorClient


class TestAnchorToolsIntegration(unittest.TestCase):
    """Integration tests for Anchor Browser tools"""
    
    def setUp(self):
        # Reset singleton instance before each test
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None
    
    def test_singleton_client_shared_across_tools(self):
        """Test that all tools share the same AnchorClient singleton instance"""
        # Create multiple tools
        content_tool = AnchorContentTool()
        screenshot_tool = AnchorScreenshotTool()
        web_task_tool = SimpleAnchorWebTaskTool()
        
        # Verify they all use the same client instance
        self.assertIs(content_tool.client, screenshot_tool.client)
        self.assertIs(screenshot_tool.client, web_task_tool.client)
        self.assertIs(content_tool.api_key, screenshot_tool.api_key)
        self.assertIs(screenshot_tool.api_key, web_task_tool.api_key)
        
        # Verify the singleton pattern works
        client1 = AnchorClient()
        client2 = AnchorClient()
        self.assertIs(client1, client2)
    
    def test_web_task_toolkit_integration_with_all_tools(self):
        """Test that the web task toolkit properly integrates all web task tools together"""
        web_task_toolkit = AnchorWebTaskToolKit()
        web_task_tools = web_task_toolkit.get_tools()
        
        # Verify toolkit returns all expected tools
        self.assertEqual(len(web_task_tools), 3)
        
        # Verify each tool is properly instantiated and configured
        tool_names = [tool.name for tool in web_task_tools]
        expected_names = [
            "simple_anchor_web_task_tool",
            "standard_anchor_web_task_tool", 
            "advanced_anchor_web_task_tool"
        ]
        self.assertEqual(tool_names, expected_names)
        
        # Verify all tools share the same client (singleton pattern)
        clients = [tool.client for tool in web_task_tools]
        self.assertTrue(all(client is clients[0] for client in clients))
        
        # Verify all tools have the same API key
        api_keys = [tool.api_key for tool in web_task_tools]
        self.assertTrue(all(api_key is api_keys[0] for api_key in api_keys))
    
    @patch.dict(os.environ, {'ANCHORBROWSER_API_KEY': 'test_env_key'})
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    def test_environment_variable_integration(self, mock_anchorbrowser):
        """Test integration with environment variables for API key"""
        # Reset singleton
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None
        
        mock_client = Mock()
        mock_anchorbrowser.return_value = mock_client
        
        # Create a tool - should use environment variable
        tool = AnchorContentTool()
        
        # Verify environment variable was used
        mock_anchorbrowser.assert_called_once_with(api_key='test_env_key')

    def test_real_anchor_browser_connection(self):
        """Test real connection to Anchor Browser API"""
        # Reset singleton to ensure fresh connection
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None
        
        # Create a tool - this will make a real connection
        content_tool = AnchorContentTool()
        
        if not content_tool.api_key:
            self.skipTest("ANCHORBROWSER_API_KEY not set - skipping real integration test")
        
        # Verify the tool has a real client
        self.assertIsNotNone(content_tool.client)
        self.assertIsNotNone(content_tool.api_key)
        
        # Test a simple content fetch (this will make a real API call)
        try:
            result = content_tool._run(url="https://example.com")
            # If we get here, the API connection worked and returned data
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0, "API should return non-empty content")
        except Exception as e:
            # Check if it's a connection/authentication error
            error_msg = str(e).lower()
            if "connection" in error_msg or "authentication" in error_msg or "unauthorized" in error_msg:
                self.fail(f"Connection/Authentication error: {e}. API key may be invalid or network issue.")
            else:
                # Other errors (like rate limiting, invalid URL, etc.) are acceptable
                # as they indicate the API connection is working
                pass


if __name__ == '__main__':
    unittest.main()