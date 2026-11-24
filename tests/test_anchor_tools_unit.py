import unittest
from unittest.mock import Mock, patch, MagicMock
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
from langchain_anchorbrowser.AnchorBaseTool import AnchorBaseTool, AnchorClient


class TestAnchorClient(unittest.TestCase):
    """Test the AnchorClient singleton pattern"""

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {'ANCHORBROWSER_API_KEY': 'env_api_key'})
    def test_environment_api_key_priority(self, mock_anchorbrowser):
        """Test that environment API key takes priority"""
        mock_anchorbrowser.return_value = Mock()

        client = AnchorClient()
        api_key, _ = client.initialize()

        self.assertEqual(api_key.get_secret_value(), 'env_api_key')
        mock_anchorbrowser.assert_called_once_with(api_key='env_api_key')


class TestAnchorBaseTool(unittest.TestCase):
    """Test the base tool functionality"""

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_base_tool_initialization(self, mock_anchorbrowser, mock_getpass):
        """Test base tool initialization"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_anchorbrowser.return_value = mock_client

        class TestTool(AnchorBaseTool):
            client_function_name = "test_function"

        tool = TestTool()

        self.assertIsNotNone(tool.api_key)
        self.assertIsNotNone(tool.client)
        self.assertEqual(tool.client_function_name, "test_function")

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_method_with_valid_function(self, mock_anchorbrowser, mock_getpass):
        """Test the _run method with a valid client function"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_tools = Mock()
        mock_client.tools = mock_tools
        mock_anchorbrowser.return_value = mock_client

        mock_session = Mock()
        mock_session_data = Mock()
        mock_session_data.id = "test_session_id"
        mock_session_data.live_view_url = "test_live_view_url"
        mock_session.data = mock_session_data
        mock_client.sessions.create_session.return_value = mock_session

        mock_function = Mock(return_value="test_result")
        mock_tools.test_function = mock_function

        class TestTool(AnchorBaseTool):
            client_function_name = "test_function"

        tool = TestTool()
        result = tool._run(url="https://example.com", param="value")

        self.assertEqual(result, "test_result")
        mock_function.assert_called_once_with(url="https://example.com", param="value", session_id="test_session_id")

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_method_missing_function_name(self, mock_anchorbrowser, mock_getpass):
        """Test _run method raises error when client_function_name is not set"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()

        class TestTool(AnchorBaseTool):
            client_function_name = None

        tool = TestTool()

        with self.assertRaises(ValueError) as context:
            tool._run(url="https://example.com")

        self.assertIn("client_function_name not set", str(context.exception))

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_method_filters_none_values(self, mock_anchorbrowser, mock_getpass):
        """Test that _run method filters out None values"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_tools = Mock()
        mock_client.tools = mock_tools
        mock_anchorbrowser.return_value = mock_client

        mock_session = Mock()
        mock_session_data = Mock()
        mock_session_data.id = "test_session_id"
        mock_session_data.live_view_url = "test_live_view_url"
        mock_session.data = mock_session_data
        mock_client.sessions.create_session.return_value = mock_session

        mock_function = Mock(return_value="test_result")
        mock_tools.test_function = mock_function

        class TestTool(AnchorBaseTool):
            client_function_name = "test_function"

        tool = TestTool()
        tool._run(url="https://example.com", param1="value", param2=None, param3="value3")

        mock_function.assert_called_once_with(url="https://example.com", param1="value", param3="value3", session_id="test_session_id")

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_uses_create_session(self, mock_anchorbrowser, mock_getpass):
        """Test that _run calls create_session (not deprecated create)"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_tools = Mock()
        mock_client.tools = mock_tools
        mock_anchorbrowser.return_value = mock_client

        mock_session = Mock()
        mock_session_data = Mock()
        mock_session_data.id = "sid-123"
        mock_session_data.live_view_url = None
        mock_session.data = mock_session_data
        mock_client.sessions.create_session.return_value = mock_session

        mock_tools.test_function = Mock(return_value="ok")

        class TestTool(AnchorBaseTool):
            client_function_name = "test_function"

        TestTool()._run(url="https://example.com")
        mock_client.sessions.create_session.assert_called_once()


class TestAnchorContentTool(unittest.TestCase):
    """Test the AnchorContentTool"""

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    def test_tool_attributes(self):
        """Test tool has correct attributes"""
        tool = AnchorContentTool()

        self.assertEqual(tool.name, "anchor_content_tool")
        self.assertIn("content", tool.description.lower())
        self.assertEqual(tool.client_function_name, "fetch_webpage")
        self.assertFalse(tool.needs_session)

    def test_input_schema_validation(self):
        """Test input schema validation"""
        tool = AnchorContentTool()
        schema = tool.args_schema

        valid_input = schema(url="https://example.com", format="markdown")
        self.assertEqual(valid_input.url, "https://example.com")
        self.assertEqual(valid_input.format, "markdown")

        valid_input_default = schema(url="https://example.com")
        self.assertEqual(valid_input_default.format, "markdown")

        with self.assertRaises(ValueError):
            schema(url="https://example.com", format="invalid_format")

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_content_tool_does_not_create_session(self, mock_anchorbrowser, mock_getpass):
        """Content tool should call fetch_webpage without creating a session"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_tools = Mock()
        mock_client.tools = mock_tools
        mock_anchorbrowser.return_value = mock_client

        mock_tools.fetch_webpage = Mock(return_value="# Example page")

        tool = AnchorContentTool()
        result = tool._run(url="https://example.com", format="markdown")

        self.assertEqual(result, "# Example page")
        mock_tools.fetch_webpage.assert_called_once_with(url="https://example.com")
        mock_client.sessions.create_session.assert_not_called()

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_content_tool_execution(self, mock_anchorbrowser, mock_getpass):
        """Test content tool execution"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_tools = Mock()
        mock_client.tools = mock_tools
        mock_anchorbrowser.return_value = mock_client

        mock_tools.fetch_webpage = Mock(return_value="<html>Test content</html>")

        tool = AnchorContentTool()
        result = tool._run(url="https://example.com", format="html")

        self.assertEqual(result, "<html>Test content</html>")
        mock_tools.fetch_webpage.assert_called_once_with(url="https://example.com")


class TestAnchorScreenshotTool(unittest.TestCase):
    """Test the AnchorScreenshotTool"""

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    def test_tool_attributes(self):
        """Test tool has correct attributes"""
        tool = AnchorScreenshotTool()

        self.assertEqual(tool.name, "anchor_screenshot_tool")
        self.assertEqual(tool.description, "Take a screenshot of a webpage using Anchor Browser")
        self.assertEqual(tool.client_function_name, "screenshot_webpage")

    def test_input_schema_validation(self):
        """Test input schema validation"""
        tool = AnchorScreenshotTool()
        schema = tool.args_schema

        valid_input = schema(url="https://example.com")
        self.assertEqual(valid_input.url, "https://example.com")
        self.assertIsNone(valid_input.width)
        self.assertIsNone(valid_input.height)

        full_input = schema(
            url="https://example.com",
            width=1920,
            height=1080,
            image_quality=90,
            wait=1000,
            scroll_all_content=True,
            capture_full_height=True,
            s3_target_address="s3://bucket/path"
        )
        self.assertEqual(full_input.width, 1920)
        self.assertEqual(full_input.height, 1080)
        self.assertEqual(full_input.image_quality, 90)
        self.assertEqual(full_input.wait, 1000)
        self.assertTrue(full_input.scroll_all_content)
        self.assertTrue(full_input.capture_full_height)
        self.assertEqual(full_input.s3_target_address, "s3://bucket/path")

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_screenshot_tool_execution(self, mock_anchorbrowser, mock_getpass):
        """Test screenshot tool execution"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_tools = Mock()
        mock_client.tools = mock_tools
        mock_anchorbrowser.return_value = mock_client

        mock_session = Mock()
        mock_session_data = Mock()
        mock_session_data.id = "test_session_id"
        mock_session_data.live_view_url = "test_live_view_url"
        mock_session.data = mock_session_data
        mock_client.sessions.create_session.return_value = mock_session

        mock_response = Mock()
        mock_response.text.return_value = "screenshot_data"
        mock_function = Mock(return_value=mock_response)
        mock_tools.screenshot_webpage = mock_function

        tool = AnchorScreenshotTool()
        result = tool._run(url="https://example.com", width=1920, height=1080)

        self.assertEqual(result, "screenshot_data")
        mock_function.assert_called_once_with(url="https://example.com", width=1920, height=1080, session_id="test_session_id")


class TestAnchorWebTaskTools(unittest.TestCase):
    """Test the Anchor Web Task Tools"""

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    def test_simple_web_task_tool(self):
        """Test SimpleAnchorWebTaskTool"""
        tool = SimpleAnchorWebTaskTool()

        self.assertEqual(tool.name, "simple_anchor_web_task_tool")
        self.assertEqual(tool.description, "Perform a simple web task using Anchor Browser AI")
        self.assertEqual(tool.client_function_name, "perform_web_task")

        schema = tool.args_schema
        valid_input = schema(prompt="Search for Python", url="https://example.com")
        self.assertEqual(valid_input.prompt, "Search for Python")
        self.assertEqual(valid_input.url, "https://example.com")

        valid_input_default = schema(prompt="Search for Python")
        self.assertEqual(valid_input_default.url, "https://example.com")

    def test_standard_web_task_tool(self):
        """Test StandardAnchorWebTaskTool"""
        tool = StandardAnchorWebTaskTool()

        self.assertEqual(tool.name, "standard_anchor_web_task_tool")
        self.assertEqual(tool.client_function_name, "perform_web_task")

        schema = tool.args_schema
        valid_input = schema(prompt="Search for Python", url="https://example.com")
        self.assertEqual(valid_input.agent, "browser-use")
        self.assertIsNone(valid_input.provider)
        self.assertIsNone(valid_input.model)

        full_input = schema(
            prompt="Search for Python",
            url="https://example.com",
            agent="openai-cua",
            provider="openai",
            model="gpt-4o-mini"
        )
        self.assertEqual(full_input.agent, "openai-cua")
        self.assertEqual(full_input.provider, "openai")
        self.assertEqual(full_input.model, "gpt-4o-mini")

    def test_advanced_web_task_tool_schema(self):
        """Test AdvancedAnchorWebTaskTool schema validation"""
        tool = AdvancedAnchorWebTaskTool()

        schema = tool.args_schema
        valid_input = schema(
            prompt="Search for Python",
            url="https://example.com",
            output_schema={"type": "object"}
        )
        self.assertEqual(valid_input.prompt, "Search for Python")
        self.assertEqual(valid_input.url, "https://example.com")

    def test_advanced_web_task_tool(self):
        """Test AdvancedAnchorWebTaskTool"""
        tool = AdvancedAnchorWebTaskTool()

        self.assertEqual(tool.name, "advanced_anchor_web_task_tool")
        self.assertEqual(tool.description, "Perform an advanced web task using Anchor Browser AI")
        self.assertEqual(tool.client_function_name, "perform_web_task")

        schema = tool.args_schema
        valid_input = schema(
            prompt="Search for Python",
            url="https://example.com",
            output_schema={"type": "object"}
        )
        self.assertEqual(valid_input.prompt, "Search for Python")
        self.assertEqual(valid_input.output_schema, {"type": "object"})

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_web_task_execution(self, mock_anchorbrowser, mock_getpass):
        """Test web task tool execution - result extracted from .data.result"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_tools = Mock()
        mock_client.tools = mock_tools
        mock_anchorbrowser.return_value = mock_client

        mock_session = Mock()
        mock_session_data = Mock()
        mock_session_data.id = "test_session_id"
        mock_session_data.live_view_url = "test_live_view_url"
        mock_session.data = mock_session_data
        mock_client.sessions.create_session.return_value = mock_session

        # Simulate PerformWebTaskSyncResponseData: .data.result is a dict
        mock_response_data = Mock()
        mock_response_data.result = {"answer": "task_result"}
        mock_response = Mock()
        mock_response.data = mock_response_data
        mock_function = Mock(return_value=mock_response)
        mock_tools.perform_web_task = mock_function

        import json
        tool = SimpleAnchorWebTaskTool()
        result = tool._run(
            prompt="Search for Python",
            url="https://example.com",
            agent="browser-use",
            provider="openai",
            model="gpt-4o-mini"
        )

        self.assertEqual(result, json.dumps({"answer": "task_result"}))
        mock_function.assert_called_once_with(
            prompt="Search for Python",
            url="https://example.com",
            agent="browser-use",
            provider="openai",
            model="gpt-4o-mini",
            session_id="test_session_id"
        )

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_web_task_without_url(self, mock_anchorbrowser, mock_getpass):
        """Test web task execution when URL is not provided"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_tools = Mock()
        mock_client.tools = mock_tools
        mock_anchorbrowser.return_value = mock_client

        mock_session = Mock()
        mock_session_data = Mock()
        mock_session_data.id = "test_session_id"
        mock_session_data.live_view_url = "test_live_view_url"
        mock_session.data = mock_session_data
        mock_client.sessions.create_session.return_value = mock_session

        mock_response_data = Mock()
        mock_response_data.result = {"answer": "task_result"}
        mock_response = Mock()
        mock_response.data = mock_response_data
        mock_function = Mock(return_value=mock_response)
        mock_tools.perform_web_task = mock_function

        tool = SimpleAnchorWebTaskTool()
        tool._run(prompt="Search for Python")

        mock_function.assert_called_once_with(
            prompt="Search for Python. Ignore the starting url.",
            url="https://example.com",
            session_id="test_session_id"
        )

    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_web_task_async_response(self, mock_anchorbrowser, mock_getpass):
        """Test web task tool with async response (no .result attribute)"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_tools = Mock()
        mock_client.tools = mock_tools
        mock_anchorbrowser.return_value = mock_client

        mock_session = Mock()
        mock_session_data = Mock()
        mock_session_data.id = "test_session_id"
        mock_session_data.live_view_url = None
        mock_session.data = mock_session_data
        mock_client.sessions.create_session.return_value = mock_session

        # Simulate async response: has status and workflow_id but not result
        mock_response_data = Mock(spec=['status', 'workflow_id', 'model_dump'])
        mock_response_data.status = "running"
        mock_response_data.workflow_id = "wf-123"
        mock_response_data.model_dump.return_value = {"status": "running", "workflow_id": "wf-123"}
        mock_response = Mock()
        mock_response.data = mock_response_data
        mock_tools.perform_web_task = Mock(return_value=mock_response)

        import json
        tool = SimpleAnchorWebTaskTool()
        result = tool._run(prompt="Search for Python", url="https://example.com")
        result_dict = json.loads(result)
        self.assertEqual(result_dict["status"], "running")
        self.assertEqual(result_dict["workflow_id"], "wf-123")


class TestAnchorWebTaskToolKit(unittest.TestCase):
    """Test the AnchorWebTaskToolKit"""

    def test_toolkit_attributes(self):
        """Test toolkit has correct attributes"""
        toolkit = AnchorWebTaskToolKit()

        self.assertEqual(toolkit.name, "anchor_web_task_tool_kit")
        self.assertEqual(toolkit.description, "Perform a web task using Anchor Browser AI")

    def test_get_tools(self):
        """Test that get_tools returns the correct tools"""
        toolkit = AnchorWebTaskToolKit()
        tools = toolkit.get_tools()

        self.assertEqual(len(tools), 3)

        tool_names = [tool.name for tool in tools]
        expected_names = [
            "simple_anchor_web_task_tool",
            "standard_anchor_web_task_tool",
            "advanced_anchor_web_task_tool"
        ]

        self.assertEqual(tool_names, expected_names)

        self.assertIsInstance(tools[0], SimpleAnchorWebTaskTool)
        self.assertIsInstance(tools[1], StandardAnchorWebTaskTool)
        self.assertIsInstance(tools[2], AdvancedAnchorWebTaskTool)


if __name__ == '__main__':
    unittest.main()
