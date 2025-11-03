from langchain_core.tools import BaseToolkit, BaseTool
from .AnchorTaskCreateTool import AnchorTaskCreateTool
from .AnchorTaskListTool import AnchorTaskListTool
from .AnchorTaskDeleteTool import AnchorTaskDeleteTool
from .AnchorTaskRunTool import AnchorTaskRunTool
from .AnchorTaskDeployTool import AnchorTaskDeployTool
from .AnchorTaskListExecutionsTool import AnchorTaskListExecutionsTool

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

