"""LangChain standard unit tests for every Anchor tool."""

from typing import ClassVar

from langchain_tests.unit_tests import ToolsUnitTests

from langchain_anchorbrowser import (
    AdvancedAnchorWebTaskTool,
    AnchorContentTool,
    AnchorScreenshotTool,
    AnchorTaskCreateTool,
    AnchorTaskDeleteTool,
    AnchorTaskDeployTool,
    AnchorTaskListExecutionsTool,
    AnchorTaskListTool,
    AnchorTaskRunTool,
    SimpleAnchorWebTaskTool,
    StandardAnchorWebTaskTool,
)


class TestAnchorContentToolStandard(ToolsUnitTests):
    tool_constructor = AnchorContentTool
    tool_invoke_params_example: ClassVar[dict] = {"url": "https://example.com"}


class TestAnchorScreenshotToolStandard(ToolsUnitTests):
    tool_constructor = AnchorScreenshotTool
    tool_invoke_params_example: ClassVar[dict] = {"url": "https://example.com", "width": 1280, "height": 720}


class TestSimpleAnchorWebTaskToolStandard(ToolsUnitTests):
    tool_constructor = SimpleAnchorWebTaskTool
    tool_invoke_params_example: ClassVar[dict] = {"prompt": "Read the main heading", "url": "https://example.com"}


class TestStandardAnchorWebTaskToolStandard(ToolsUnitTests):
    tool_constructor = StandardAnchorWebTaskTool
    tool_invoke_params_example: ClassVar[dict] = {"prompt": "Read the main heading", "agent": "browser-use"}


class TestAdvancedAnchorWebTaskToolStandard(ToolsUnitTests):
    tool_constructor = AdvancedAnchorWebTaskTool
    tool_invoke_params_example: ClassVar[dict] = {
        "prompt": "Read the main heading",
        "output_schema": {"type": "object", "properties": {"heading": {"type": "string"}}},
    }


class TestAnchorTaskCreateToolStandard(ToolsUnitTests):
    tool_constructor = AnchorTaskCreateTool
    tool_invoke_params_example: ClassVar[dict] = {"name": "demo-task", "language": "typescript"}


class TestAnchorTaskListToolStandard(ToolsUnitTests):
    tool_constructor = AnchorTaskListTool
    tool_invoke_params_example: ClassVar[dict] = {"page": "1", "limit": "10"}


class TestAnchorTaskDeployToolStandard(ToolsUnitTests):
    tool_constructor = AnchorTaskDeployTool
    tool_invoke_params_example: ClassVar[dict] = {"task_id": "task-1", "code": "ZXhwb3J0IGRlZmF1bHQge30="}


class TestAnchorTaskRunToolStandard(ToolsUnitTests):
    tool_constructor = AnchorTaskRunTool
    tool_invoke_params_example: ClassVar[dict] = {"task_id": "task-1", "version": "latest"}


class TestAnchorTaskListExecutionsToolStandard(ToolsUnitTests):
    tool_constructor = AnchorTaskListExecutionsTool
    tool_invoke_params_example: ClassVar[dict] = {"task_id": "task-1", "status": "success"}


class TestAnchorTaskDeleteToolStandard(ToolsUnitTests):
    tool_constructor = AnchorTaskDeleteTool
    tool_invoke_params_example: ClassVar[dict] = {"task_id": "task-1"}
