import importlib
import json
import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_anchorbrowser.AnchorBaseTool import AnchorClient
from langchain_anchorbrowser.AnchorTaskCreateTool import AnchorTaskCreateTool
from langchain_anchorbrowser.AnchorTaskDeleteTool import AnchorTaskDeleteTool
from langchain_anchorbrowser.AnchorTaskDeployTool import AnchorTaskDeployTool
from langchain_anchorbrowser.AnchorTaskListExecutionsTool import AnchorTaskListExecutionsTool
from langchain_anchorbrowser.AnchorTaskListTool import AnchorTaskListTool
from langchain_anchorbrowser.AnchorTaskRunTool import AnchorTaskRunTool
from langchain_anchorbrowser.AnchorTaskToolKit import AnchorTaskToolKit

# The package re-exports a class named like this module, so on Python 3.10 a dotted
# patch target such as "langchain_anchorbrowser.AnchorBaseTool.X" resolves to the class.
base_tool_module = importlib.import_module("langchain_anchorbrowser.AnchorBaseTool")


def _make_mock_client(mock_anchorbrowser):
    """Return a fully-configured mock Anchorbrowser client."""
    mock_client = Mock()
    mock_anchorbrowser.return_value = mock_client
    return mock_client


class TestAnchorTaskCreateTool(unittest.TestCase):

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskCreateTool()

        self.assertEqual(tool.name, "create_task")
        self.assertIn("Create a new task", tool.description)
        self.assertIsNone(tool.client_function_name)

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskCreateTool()
        schema = tool.args_schema

        valid_input = schema(name="my-task")
        self.assertEqual(valid_input.name, "my-task")
        self.assertEqual(valid_input.language, "typescript")
        self.assertIsNone(valid_input.description)
        self.assertIsNone(valid_input.code)

        full_input = schema(name="my-task", description="A test task", code="base64code", language="typescript")
        self.assertEqual(full_input.name, "my-task")
        self.assertEqual(full_input.description, "A test task")
        self.assertEqual(full_input.code, "base64code")

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_create_task_execution(self, mock_anchorbrowser, mock_getpass):
        """Test that create_task calls tasks_legacy.create_task"""
        mock_getpass.return_value = "test_api_key"
        mock_client = _make_mock_client(mock_anchorbrowser)

        mock_data = Mock()
        mock_data.model_dump.return_value = {"id": "task-123", "name": "my-task", "language": "typescript"}
        mock_response = Mock()
        mock_response.data = mock_data
        mock_client.tasks_legacy.create_task.return_value = mock_response

        tool = AnchorTaskCreateTool()
        result = tool._run(name="my-task", description="A test task", language="typescript")

        result_dict = json.loads(result)
        self.assertEqual(result_dict["id"], "task-123")
        self.assertEqual(result_dict["name"], "my-task")

        mock_client.tasks_legacy.create_task.assert_called_once_with(
            name="my-task",
            language="typescript",
            description="A test task",
            code=None,
        )

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_create_task_missing_name(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskCreateTool()

        with self.assertRaises(ValueError) as context:
            tool._run(description="A test task")

        self.assertIn("Task name is required", str(context.exception))


class TestAnchorTaskListTool(unittest.TestCase):

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskListTool()

        self.assertEqual(tool.name, "list_tasks")
        self.assertIn("List all tasks", tool.description)
        self.assertIsNone(tool.client_function_name)

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskListTool()
        schema = tool.args_schema

        valid_input = schema()
        self.assertEqual(valid_input.page, "1")
        self.assertEqual(valid_input.limit, "10")

        custom_input = schema(page="2", limit="20")
        self.assertEqual(custom_input.page, "2")
        self.assertEqual(custom_input.limit, "20")

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_tasks_execution(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        mock_client = _make_mock_client(mock_anchorbrowser)

        mock_data = Mock()
        mock_data.model_dump.return_value = {"tasks": [{"id": "task-1", "name": "task1"}], "total": 1, "page": 1, "limit": 10}
        mock_response = Mock()
        mock_response.data = mock_data
        mock_client.tasks_legacy.list_tasks.return_value = mock_response

        tool = AnchorTaskListTool()
        result = tool._run(page="1", limit="10")

        result_dict = json.loads(result)
        self.assertIn("tasks", result_dict)
        self.assertEqual(len(result_dict["tasks"]), 1)

        mock_client.tasks_legacy.list_tasks.assert_called_once_with(page="1", limit="10")

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_tasks_with_defaults(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        mock_client = _make_mock_client(mock_anchorbrowser)

        mock_data = Mock()
        mock_data.model_dump.return_value = {"tasks": [], "total": 0}
        mock_response = Mock()
        mock_response.data = mock_data
        mock_client.tasks_legacy.list_tasks.return_value = mock_response

        tool = AnchorTaskListTool()
        tool._run()

        mock_client.tasks_legacy.list_tasks.assert_called_once_with(page="1", limit="10")


class TestAnchorTaskDeleteTool(unittest.TestCase):

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskDeleteTool()

        self.assertEqual(tool.name, "delete_task")
        self.assertIn("Delete a task", tool.description)
        self.assertIsNone(tool.client_function_name)

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskDeleteTool()
        schema = tool.args_schema

        valid_input = schema(task_id="task-123")
        self.assertEqual(valid_input.task_id, "task-123")

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_delete_task_execution(self, mock_anchorbrowser, mock_getpass):
        """Test that delete_task calls tasks_legacy.delete_task (SDK, not httpx)"""
        mock_getpass.return_value = "test_api_key"
        mock_client = _make_mock_client(mock_anchorbrowser)

        mock_data = Mock()
        mock_data.model_dump.return_value = {"success": True, "message": "Task deleted"}
        mock_response = Mock()
        mock_response.data = mock_data
        mock_client.tasks_legacy.delete_task.return_value = mock_response

        tool = AnchorTaskDeleteTool()
        result = tool._run(task_id="task-123")

        result_dict = json.loads(result)
        self.assertTrue(result_dict["success"])

        mock_client.tasks_legacy.delete_task.assert_called_once_with("task-123")

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_delete_task_missing_task_id(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskDeleteTool()

        with self.assertRaises(ValueError) as context:
            tool._run()

        self.assertIn("task_id is required", str(context.exception))


class TestAnchorTaskRunTool(unittest.TestCase):

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskRunTool()

        self.assertEqual(tool.name, "run_task")
        self.assertIn("Execute a task", tool.description)
        self.assertIsNone(tool.client_function_name)

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskRunTool()
        schema = tool.args_schema

        valid_input = schema(task_id="task-123")
        self.assertEqual(valid_input.task_id, "task-123")
        self.assertEqual(valid_input.version, "latest")
        self.assertIsNone(valid_input.session_id)
        self.assertIsNone(valid_input.inputs)

        full_input = schema(
            task_id="task-123",
            version="1",
            session_id="session-456",
            inputs='{"ANCHOR_TARGET_URL": "https://example.com"}'
        )
        self.assertEqual(full_input.version, "1")
        self.assertEqual(full_input.session_id, "session-456")

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_task_execution(self, mock_anchorbrowser, mock_getpass):
        """Test that run_task calls tasks_legacy.run_adhoc_task"""
        mock_getpass.return_value = "test_api_key"
        mock_client = _make_mock_client(mock_anchorbrowser)

        mock_data = Mock()
        mock_data.model_dump.return_value = {"task_id": "task-123", "execution_time": 5.0, "output": "done"}
        mock_response = Mock()
        mock_response.data = mock_data
        mock_client.tasks_legacy.run_adhoc_task.return_value = mock_response

        tool = AnchorTaskRunTool()
        result = tool._run(task_id="task-123", version="1")

        result_dict = json.loads(result)
        self.assertEqual(result_dict["task_id"], "task-123")

        mock_client.tasks_legacy.run_adhoc_task.assert_called_once_with(
            task_id="task-123",
            version="1"
        )

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_task_with_inputs(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        mock_client = _make_mock_client(mock_anchorbrowser)

        mock_data = Mock()
        mock_data.model_dump.return_value = {"task_id": "task-123"}
        mock_response = Mock()
        mock_response.data = mock_data
        mock_client.tasks_legacy.run_adhoc_task.return_value = mock_response

        tool = AnchorTaskRunTool()
        inputs_json = '{"ANCHOR_TARGET_URL": "https://example.com", "ANCHOR_MAX_PAGES": "10"}'
        tool._run(task_id="task-123", version="1", inputs=inputs_json)

        mock_client.tasks_legacy.run_adhoc_task.assert_called_once_with(
            task_id="task-123",
            version="1",
            inputs={"ANCHOR_TARGET_URL": "https://example.com", "ANCHOR_MAX_PAGES": "10"}
        )

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_task_invalid_json_inputs(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskRunTool()

        with self.assertRaises(ValueError) as context:
            tool._run(task_id="task-123", inputs="invalid json{")

        self.assertIn("Invalid JSON in inputs", str(context.exception))

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_run_task_missing_task_id(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskRunTool()

        with self.assertRaises(ValueError) as context:
            tool._run(version="1")

        self.assertIn("task_id is required", str(context.exception))


class TestAnchorTaskDeployTool(unittest.TestCase):

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskDeployTool()

        self.assertEqual(tool.name, "deploy_task")
        self.assertIn("Deploy a task version", tool.description)
        self.assertIsNone(tool.client_function_name)

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskDeployTool()
        schema = tool.args_schema

        valid_input = schema(task_id="task-123")
        self.assertEqual(valid_input.task_id, "task-123")
        self.assertEqual(valid_input.language, "typescript")
        self.assertIsNone(valid_input.code)
        self.assertIsNone(valid_input.description)

        full_input = schema(task_id="task-123", code="base64code", language="typescript", description="v1.0")
        self.assertEqual(full_input.code, "base64code")
        self.assertEqual(full_input.description, "v1.0")

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_deploy_task_execution(self, mock_anchorbrowser, mock_getpass):
        """Test that deploy_task calls tasks_legacy.deploy_task (SDK, not httpx)"""
        mock_getpass.return_value = "test_api_key"
        mock_client = _make_mock_client(mock_anchorbrowser)

        mock_data = Mock()
        mock_data.model_dump.return_value = {"version": "1.0", "task_id": "task-123", "code": "base64code"}
        mock_response = Mock()
        mock_response.data = mock_data
        mock_client.tasks_legacy.deploy_task.return_value = mock_response

        tool = AnchorTaskDeployTool()
        result = tool._run(task_id="task-123", code="base64code", language="typescript")

        result_dict = json.loads(result)
        self.assertEqual(result_dict["version"], "1.0")

        mock_client.tasks_legacy.deploy_task.assert_called_once_with(
            task_id="task-123",
            code="base64code",
            language="typescript",
        )

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_deploy_task_missing_task_id(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskDeployTool()

        with self.assertRaises(ValueError) as context:
            tool._run(code="base64code")

        self.assertIn("task_id is required", str(context.exception))


class TestAnchorTaskListExecutionsTool(unittest.TestCase):

    def setUp(self):
        AnchorClient._instance = None
        AnchorClient._client = None
        AnchorClient._api_key = None

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_tool_attributes(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskListExecutionsTool()

        self.assertEqual(tool.name, "list_task_executions")
        self.assertIn("List task execution results", tool.description)
        self.assertIsNone(tool.client_function_name)

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_input_schema_validation(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskListExecutionsTool()
        schema = tool.args_schema

        valid_input = schema(task_id="task-123")
        self.assertEqual(valid_input.task_id, "task-123")
        self.assertEqual(valid_input.page, "1")
        self.assertEqual(valid_input.limit, "10")
        self.assertIsNone(valid_input.status)
        self.assertIsNone(valid_input.version)

        full_input = schema(task_id="task-123", page="2", limit="20", status="success", version="1.0")
        self.assertEqual(full_input.page, "2")
        self.assertEqual(full_input.status, "success")
        self.assertEqual(full_input.version, "1.0")

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_executions_execution(self, mock_anchorbrowser, mock_getpass):
        """Test that list_task_executions calls tasks_legacy.list_task_executions (SDK, not httpx)"""
        mock_getpass.return_value = "test_api_key"
        mock_client = _make_mock_client(mock_anchorbrowser)

        mock_data = Mock()
        mock_data.model_dump.return_value = {
            "results": [{"id": "exec-1", "status": "success"}],
            "pagination": {"page": 1, "limit": 10}
        }
        mock_response = Mock()
        mock_response.data = mock_data
        mock_client.tasks_legacy.list_task_executions.return_value = mock_response

        tool = AnchorTaskListExecutionsTool()
        result = tool._run(task_id="task-123", page="1", limit="10")

        result_dict = json.loads(result)
        self.assertIn("results", result_dict)
        self.assertEqual(len(result_dict["results"]), 1)

        mock_client.tasks_legacy.list_task_executions.assert_called_once_with(
            task_id="task-123", page="1", limit="10"
        )

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_executions_with_filters(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        mock_client = _make_mock_client(mock_anchorbrowser)

        mock_data = Mock()
        mock_data.model_dump.return_value = {"results": []}
        mock_response = Mock()
        mock_response.data = mock_data
        mock_client.tasks_legacy.list_task_executions.return_value = mock_response

        tool = AnchorTaskListExecutionsTool()
        tool._run(task_id="task-123", status="success", version="1")

        call_kwargs = mock_client.tasks_legacy.list_task_executions.call_args[1]
        self.assertEqual(call_kwargs["status"], "success")
        self.assertEqual(call_kwargs["version"], "1")

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_executions_filters_empty_strings(self, mock_anchorbrowser, mock_getpass):
        """Empty strings for status/version should not be passed to the API"""
        mock_getpass.return_value = "test_api_key"
        mock_client = _make_mock_client(mock_anchorbrowser)

        mock_data = Mock()
        mock_data.model_dump.return_value = {"results": []}
        mock_response = Mock()
        mock_response.data = mock_data
        mock_client.tasks_legacy.list_task_executions.return_value = mock_response

        tool = AnchorTaskListExecutionsTool()
        tool._run(task_id="task-123", status="", version="")

        call_kwargs = mock_client.tasks_legacy.list_task_executions.call_args[1]
        self.assertNotIn("status", call_kwargs)
        self.assertNotIn("version", call_kwargs)

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_list_executions_missing_task_id(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        _make_mock_client(mock_anchorbrowser)

        tool = AnchorTaskListExecutionsTool()

        with self.assertRaises(ValueError) as context:
            tool._run(page="1")

        self.assertIn("task_id is required", str(context.exception))


class TestAnchorTaskToolKit(unittest.TestCase):

    def test_toolkit_attributes(self):
        toolkit = AnchorTaskToolKit()

        self.assertEqual(toolkit.name, "anchor_task_tool_kit")
        self.assertIn("Tools for managing and executing", toolkit.description)

    @patch('getpass.getpass')
    @patch.object(base_tool_module, 'Anchorbrowser')
    @patch.dict(os.environ, {}, clear=True)
    def test_get_tools(self, mock_anchorbrowser, mock_getpass):
        mock_getpass.return_value = "test_api_key"
        Mock()

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

        self.assertIsInstance(tools[0], AnchorTaskCreateTool)
        self.assertIsInstance(tools[1], AnchorTaskListTool)
        self.assertIsInstance(tools[2], AnchorTaskDeleteTool)
        self.assertIsInstance(tools[3], AnchorTaskRunTool)
        self.assertIsInstance(tools[4], AnchorTaskDeployTool)
        self.assertIsInstance(tools[5], AnchorTaskListExecutionsTool)


if __name__ == '__main__':
    unittest.main()
