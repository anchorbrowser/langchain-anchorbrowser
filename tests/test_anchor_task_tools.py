import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_anchorbrowser.AnchorTaskCreateTool import AnchorTaskCreateTool
from langchain_anchorbrowser.AnchorTaskListTool import AnchorTaskListTool
from langchain_anchorbrowser.AnchorTaskDeleteTool import AnchorTaskDeleteTool
from langchain_anchorbrowser.AnchorTaskRunTool import AnchorTaskRunTool
from langchain_anchorbrowser.AnchorTaskDeployTool import AnchorTaskDeployTool
from langchain_anchorbrowser.AnchorTaskListExecutionsTool import AnchorTaskListExecutionsTool
from langchain_anchorbrowser.AnchorTaskToolKit import AnchorTaskToolKit
from langchain_anchorbrowser.AnchorBaseTool import AnchorBaseTool, AnchorClient


class TestAnchorTaskCreateTool(unittest.TestCase):
    """Test the AnchorTaskCreateTool"""
    
    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        """Test tool has correct attributes"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskCreateTool()
        
        self.assertEqual(tool.name, "create_task")
        self.assertIn("Create a new task", tool.description)
        self.assertIsNone(tool.client_function_name)
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        """Test input schema validation"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskCreateTool()
        schema = tool.args_schema
        
        # Test minimal valid input (name is required)
        valid_input = schema(name="my-task")
        self.assertEqual(valid_input.name, "my-task")
        self.assertEqual(valid_input.language, "typescript")
        self.assertIsNone(valid_input.description)
        self.assertIsNone(valid_input.code)
        
        # Test full valid input
        full_input = schema(
            name="my-task",
            description="A test task",
            code="base64encodedcode",
            language="typescript"
        )
        self.assertEqual(full_input.name, "my-task")
        self.assertEqual(full_input.description, "A test task")
        self.assertEqual(full_input.code, "base64encodedcode")
        self.assertEqual(full_input.language, "typescript")
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_create_task_execution(self, mock_anchorbrowser, mock_getpass):
        """Test create task execution"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_task_resource = Mock()
        mock_client.task = mock_task_resource
        mock_anchorbrowser.return_value = mock_client
        
        mock_response = Mock()
        mock_response.model_dump.return_value = {
            "id": "task-123",
            "name": "my-task",
            "language": "typescript"
        }
        mock_task_resource.create.return_value = mock_response
        
        tool = AnchorTaskCreateTool()
        result = tool._run(name="my-task", description="A test task", language="typescript")
        
        result_dict = json.loads(result)
        self.assertEqual(result_dict["id"], "task-123")
        self.assertEqual(result_dict["name"], "my-task")
        
        mock_task_resource.create.assert_called_once_with(
            name="my-task",
            language="typescript",
            description="A test task",
            code=None
        )
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_create_task_missing_name(self, mock_anchorbrowser, mock_getpass):
        """Test create task raises error when name is missing"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskCreateTool()
        
        with self.assertRaises(ValueError) as context:
            tool._run(description="A test task")
        
        self.assertIn("Task name is required", str(context.exception))


class TestAnchorTaskListTool(unittest.TestCase):
    """Test the AnchorTaskListTool"""
    
    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        """Test tool has correct attributes"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskListTool()
        
        self.assertEqual(tool.name, "list_tasks")
        self.assertIn("List all tasks", tool.description)
        self.assertIsNone(tool.client_function_name)
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        """Test input schema validation"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskListTool()
        schema = tool.args_schema
        
        # Test with defaults
        valid_input = schema()
        self.assertEqual(valid_input.page, "1")
        self.assertEqual(valid_input.limit, "10")
        
        # Test custom values
        custom_input = schema(page="2", limit="20")
        self.assertEqual(custom_input.page, "2")
        self.assertEqual(custom_input.limit, "20")
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_tasks_execution(self, mock_anchorbrowser, mock_getpass):
        """Test list tasks execution"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_task_resource = Mock()
        mock_client.task = mock_task_resource
        mock_anchorbrowser.return_value = mock_client
        
        mock_response = Mock()
        mock_response.model_dump.return_value = {
            "items": [{"id": "task-1", "name": "task1"}],
            "pagination": {"page": 1, "limit": 10}
        }
        mock_task_resource.list.return_value = mock_response
        
        tool = AnchorTaskListTool()
        result = tool._run(page="1", limit="10")
        
        result_dict = json.loads(result)
        self.assertIn("items", result_dict)
        self.assertEqual(len(result_dict["items"]), 1)
        
        mock_task_resource.list.assert_called_once_with(page="1", limit="10")
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_tasks_with_defaults(self, mock_anchorbrowser, mock_getpass):
        """Test list tasks with default pagination"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_task_resource = Mock()
        mock_client.task = mock_task_resource
        mock_anchorbrowser.return_value = mock_client
        
        mock_response = Mock()
        mock_response.model_dump.return_value = {"items": []}
        mock_task_resource.list.return_value = mock_response
        
        tool = AnchorTaskListTool()
        tool._run()
        
        mock_task_resource.list.assert_called_once_with(page="1", limit="10")


class TestAnchorTaskDeleteTool(unittest.TestCase):
    """Test the AnchorTaskDeleteTool"""
    
    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        """Test tool has correct attributes"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskDeleteTool()
        
        self.assertEqual(tool.name, "delete_task")
        self.assertIn("Delete a task", tool.description)
        self.assertIsNone(tool.client_function_name)
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        """Test input schema validation"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskDeleteTool()
        schema = tool.args_schema
        
        # Test valid input
        valid_input = schema(task_id="task-123")
        self.assertEqual(valid_input.task_id, "task-123")
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch('httpx.Client')
    @patch.dict(os.environ, {}, clear=True)
    def test_delete_task_execution(self, mock_httpx_client, mock_anchorbrowser, mock_getpass):
        """Test delete task execution"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_client._client._base_url = Mock()
        mock_client._client._base_url.__str__ = Mock(return_value="https://api.anchorbrowser.io/")
        mock_anchorbrowser.return_value = mock_client
        
        # Mock httpx client
        mock_http_client = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_http_client)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_httpx_client.return_value = mock_context_manager
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_http_client.delete.return_value = mock_response
        
        tool = AnchorTaskDeleteTool()
        result = tool._run(task_id="task-123")
        
        result_dict = json.loads(result)
        self.assertTrue(result_dict["success"])
        self.assertEqual(result_dict["task_id"], "task-123")
        
        mock_http_client.delete.assert_called_once()
        call_args = mock_http_client.delete.call_args
        self.assertIn("task-123", call_args[0][0])
        self.assertIn("anchor-api-key", call_args[1]["headers"])
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_delete_task_missing_task_id(self, mock_anchorbrowser, mock_getpass):
        """Test delete task raises error when task_id is missing"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskDeleteTool()
        
        with self.assertRaises(ValueError) as context:
            tool._run()
        
        self.assertIn("task_id is required", str(context.exception))


class TestAnchorTaskRunTool(unittest.TestCase):
    """Test the AnchorTaskRunTool"""
    
    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        """Test tool has correct attributes"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskRunTool()
        
        self.assertEqual(tool.name, "run_task")
        self.assertIn("Execute a task", tool.description)
        self.assertIsNone(tool.client_function_name)
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        """Test input schema validation"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskRunTool()
        schema = tool.args_schema
        
        # Test minimal valid input
        valid_input = schema(task_id="task-123")
        self.assertEqual(valid_input.task_id, "task-123")
        self.assertEqual(valid_input.version, "latest")  # Default is still "latest"
        self.assertIsNone(valid_input.session_id)
        self.assertIsNone(valid_input.inputs)
        
        # Test full valid input (using version "1" as in deployment scenario and script inputs)
        full_input = schema(
            task_id="task-123",
            version="1",
            session_id="session-456",
            inputs='{"ANCHOR_TARGET_URL": "https://example.com", "ANCHOR_MAX_PAGES": "10"}'
        )
        self.assertEqual(full_input.task_id, "task-123")
        self.assertEqual(full_input.version, "1")
        self.assertEqual(full_input.session_id, "session-456")
        self.assertEqual(full_input.inputs, '{"ANCHOR_TARGET_URL": "https://example.com", "ANCHOR_MAX_PAGES": "10"}')
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_task_execution(self, mock_anchorbrowser, mock_getpass):
        """Test run task execution"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_task_resource = Mock()
        mock_task_resource.run = Mock()
        mock_client.task = mock_task_resource
        mock_anchorbrowser.return_value = mock_client
        
        mock_response = Mock()
        mock_response.model_dump.return_value = {
            "execution_id": "exec-123",
            "status": "running"
        }
        mock_task_resource.run.return_value = mock_response
        
        tool = AnchorTaskRunTool()
        result = tool._run(task_id="task-123", version="1")
        
        result_dict = json.loads(result)
        self.assertEqual(result_dict["execution_id"], "exec-123")
        self.assertEqual(result_dict["status"], "running")
        
        mock_task_resource.run.assert_called_once_with(
            task_id="task-123",
            version="1"
        )
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_task_with_inputs(self, mock_anchorbrowser, mock_getpass):
        """Test run task with JSON inputs"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_task_resource = Mock()
        mock_task_resource.run = Mock()
        mock_client.task = mock_task_resource
        mock_anchorbrowser.return_value = mock_client
        
        mock_response = Mock()
        mock_response.model_dump.return_value = {"execution_id": "exec-123"}
        mock_task_resource.run.return_value = mock_response
        
        tool = AnchorTaskRunTool()
        inputs_json = '{"ANCHOR_TARGET_URL": "https://example.com", "ANCHOR_MAX_PAGES": "10"}'
        tool._run(task_id="task-123", version="1", inputs=inputs_json)
        
        mock_task_resource.run.assert_called_once_with(
            task_id="task-123",
            version="1",
            inputs={"ANCHOR_TARGET_URL": "https://example.com", "ANCHOR_MAX_PAGES": "10"}
        )
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_task_invalid_json_inputs(self, mock_anchorbrowser, mock_getpass):
        """Test run task with invalid JSON inputs"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskRunTool()
        
        with self.assertRaises(ValueError) as context:
            tool._run(task_id="task-123", inputs="invalid json{")
        
        self.assertIn("Invalid JSON in inputs", str(context.exception))
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_task_missing_task_id(self, mock_anchorbrowser, mock_getpass):
        """Test run task raises error when task_id is missing"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskRunTool()
        
        with self.assertRaises(ValueError) as context:
            tool._run(version="1")
        
        self.assertIn("task_id is required", str(context.exception))


class TestAnchorTaskDeployTool(unittest.TestCase):
    """Test the AnchorTaskDeployTool"""
    
    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        """Test tool has correct attributes"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskDeployTool()
        
        self.assertEqual(tool.name, "deploy_task")
        self.assertIn("Deploy a task version", tool.description)
        self.assertIsNone(tool.client_function_name)
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        """Test input schema validation"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskDeployTool()
        schema = tool.args_schema
        
        # Test minimal valid input
        valid_input = schema(task_id="task-123")
        self.assertEqual(valid_input.task_id, "task-123")
        self.assertEqual(valid_input.language, "typescript")
        self.assertIsNone(valid_input.code)
        self.assertIsNone(valid_input.description)
        
        # Test full valid input
        full_input = schema(
            task_id="task-123",
            code="base64code",
            language="typescript",
            description="Version 1.0"
        )
        self.assertEqual(full_input.task_id, "task-123")
        self.assertEqual(full_input.code, "base64code")
        self.assertEqual(full_input.language, "typescript")
        self.assertEqual(full_input.description, "Version 1.0")
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch('httpx.Client')
    @patch.dict(os.environ, {}, clear=True)
    def test_deploy_task_execution(self, mock_httpx_client, mock_anchorbrowser, mock_getpass):
        """Test deploy task execution"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_client._client._base_url = Mock()
        mock_client._client._base_url.__str__ = Mock(return_value="https://api.anchorbrowser.io/")
        mock_anchorbrowser.return_value = mock_client
        
        # Mock httpx client
        mock_http_client = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_http_client)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_httpx_client.return_value = mock_context_manager
        
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"version": "1.0", "task_id": "task-123"}
        mock_response.raise_for_status = Mock()
        mock_http_client.post.return_value = mock_response
        
        tool = AnchorTaskDeployTool()
        result = tool._run(task_id="task-123", code="base64code", language="typescript")
        
        result_dict = json.loads(result)
        self.assertEqual(result_dict["version"], "1.0")
        self.assertEqual(result_dict["task_id"], "task-123")
        
        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        self.assertIn("task-123", call_args[0][0])
        self.assertIn("anchor-api-key", call_args[1]["headers"])
        self.assertEqual(call_args[1]["json"]["code"], "base64code")
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_deploy_task_missing_task_id(self, mock_anchorbrowser, mock_getpass):
        """Test deploy task raises error when task_id is missing"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskDeployTool()
        
        with self.assertRaises(ValueError) as context:
            tool._run(code="base64code")
        
        self.assertIn("task_id is required", str(context.exception))


class TestAnchorTaskListExecutionsTool(unittest.TestCase):
    """Test the AnchorTaskListExecutionsTool"""
    
    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        """Test tool has correct attributes"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskListExecutionsTool()
        
        self.assertEqual(tool.name, "list_task_executions")
        self.assertIn("List task execution results", tool.description)
        self.assertIsNone(tool.client_function_name)
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        """Test input schema validation"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskListExecutionsTool()
        schema = tool.args_schema
        
        # Test minimal valid input
        valid_input = schema(task_id="task-123")
        self.assertEqual(valid_input.task_id, "task-123")
        self.assertEqual(valid_input.page, "1")
        self.assertEqual(valid_input.limit, "10")
        self.assertIsNone(valid_input.status)
        self.assertIsNone(valid_input.version)
        
        # Test full valid input
        full_input = schema(
            task_id="task-123",
            page="2",
            limit="20",
            status="success",
            version="1.0"
        )
        self.assertEqual(full_input.task_id, "task-123")
        self.assertEqual(full_input.page, "2")
        self.assertEqual(full_input.limit, "20")
        self.assertEqual(full_input.status, "success")
        self.assertEqual(full_input.version, "1.0")
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch('httpx.Client')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_executions_execution(self, mock_httpx_client, mock_anchorbrowser, mock_getpass):
        """Test list executions execution"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_client._client._base_url = Mock()
        mock_client._client._base_url.__str__ = Mock(return_value="https://api.anchorbrowser.io/")
        mock_anchorbrowser.return_value = mock_client
        
        # Mock httpx client
        mock_http_client = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_http_client)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_httpx_client.return_value = mock_context_manager
        
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": "exec-1", "status": "success"}],
            "pagination": {"page": 1, "limit": 10}
        }
        mock_response.raise_for_status = Mock()
        mock_http_client.get.return_value = mock_response
        
        tool = AnchorTaskListExecutionsTool()
        result = tool._run(task_id="task-123", page="1", limit="10")
        
        result_dict = json.loads(result)
        self.assertIn("results", result_dict)
        self.assertEqual(len(result_dict["results"]), 1)
        
        mock_http_client.get.assert_called_once()
        call_args = mock_http_client.get.call_args
        self.assertIn("task-123", call_args[0][0])
        self.assertEqual(call_args[1]["params"]["page"], "1")
        self.assertEqual(call_args[1]["params"]["limit"], "10")
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch('httpx.Client')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_executions_with_filters(self, mock_httpx_client, mock_anchorbrowser, mock_getpass):
        """Test list executions with status and version filters"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_client._client._base_url = Mock()
        mock_client._client._base_url.__str__ = Mock(return_value="https://api.anchorbrowser.io/")
        mock_anchorbrowser.return_value = mock_client
        
        # Mock httpx client
        mock_http_client = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_http_client)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_httpx_client.return_value = mock_context_manager
        
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_http_client.get.return_value = mock_response
        
        tool = AnchorTaskListExecutionsTool()
        tool._run(task_id="task-123", status="success", version="1")
        
        call_args = mock_http_client.get.call_args
        params = call_args[1]["params"]
        self.assertEqual(params["status"], "success")
        self.assertEqual(params["version"], "1")
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch('httpx.Client')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_executions_filters_empty_strings(self, mock_httpx_client, mock_anchorbrowser, mock_getpass):
        """Test that empty string filters are not included in query params"""
        mock_getpass.return_value = "test_api_key"
        mock_client = Mock()
        mock_client._client._base_url = Mock()
        mock_client._client._base_url.__str__ = Mock(return_value="https://api.anchorbrowser.io/")
        mock_anchorbrowser.return_value = mock_client
        
        # Mock httpx client
        mock_http_client = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_http_client)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_httpx_client.return_value = mock_context_manager
        
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_http_client.get.return_value = mock_response
        
        tool = AnchorTaskListExecutionsTool()
        tool._run(task_id="task-123", status="", version="")
        
        call_args = mock_http_client.get.call_args
        params = call_args[1]["params"]
        self.assertNotIn("status", params)
        self.assertNotIn("version", params)
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_executions_missing_task_id(self, mock_anchorbrowser, mock_getpass):
        """Test list executions raises error when task_id is missing"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        tool = AnchorTaskListExecutionsTool()
        
        with self.assertRaises(ValueError) as context:
            tool._run(page="1")
        
        self.assertIn("task_id is required", str(context.exception))


class TestAnchorTaskToolKit(unittest.TestCase):
    """Test the AnchorTaskToolKit"""
    
    def test_toolkit_attributes(self):
        """Test toolkit has correct attributes"""
        toolkit = AnchorTaskToolKit()
        
        self.assertEqual(toolkit.name, "anchor_task_tool_kit")
        self.assertIn("Tools for managing and executing", toolkit.description)
    
    @patch('langchain_anchorbrowser.AnchorBaseTool.getpass.getpass')
    @patch('langchain_anchorbrowser.AnchorBaseTool.Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_get_tools(self, mock_anchorbrowser, mock_getpass):
        """Test that get_tools returns the correct tools"""
        mock_getpass.return_value = "test_api_key"
        mock_anchorbrowser.return_value = Mock()
        
        toolkit = AnchorTaskToolKit()
        tools = toolkit.get_tools()
        
        self.assertEqual(len(tools), 6)
        
        tool_names = [tool.name for tool in tools]
        expected_names = [
            "create_task",
            "list_tasks",
            "delete_task",
            "run_task",
            "deploy_task",
            "list_task_executions"
        ]
        
        self.assertEqual(tool_names, expected_names)
        
        # Verify tool types
        self.assertIsInstance(tools[0], AnchorTaskCreateTool)
        self.assertIsInstance(tools[1], AnchorTaskListTool)
        self.assertIsInstance(tools[2], AnchorTaskDeleteTool)
        self.assertIsInstance(tools[3], AnchorTaskRunTool)
        self.assertIsInstance(tools[4], AnchorTaskDeployTool)
        self.assertIsInstance(tools[5], AnchorTaskListExecutionsTool)


if __name__ == '__main__':
    unittest.main()

