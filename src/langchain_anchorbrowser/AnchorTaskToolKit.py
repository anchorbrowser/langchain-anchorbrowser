from langchain_core.tools import BaseTool, BaseToolkit

from .AnchorTaskCreateTool import AnchorTaskCreateTool
from .AnchorTaskDeleteTool import AnchorTaskDeleteTool
from .AnchorTaskDeployTool import AnchorTaskDeployTool
from .AnchorTaskListExecutionsTool import AnchorTaskListExecutionsTool
from .AnchorTaskListTool import AnchorTaskListTool
from .AnchorTaskRunTool import AnchorTaskRunTool


class AnchorTaskToolKit(BaseToolkit):
    name: str = "anchor_task_tool_kit"
    description: str = "Tools for managing and executing Anchor Browser tasks"

    def get_tools(self) -> list[BaseTool]:
        return [
            AnchorTaskCreateTool(),
            AnchorTaskListTool(),
            AnchorTaskDeleteTool(),
            AnchorTaskRunTool(),
            AnchorTaskDeployTool(),
            AnchorTaskListExecutionsTool(),
        ]

