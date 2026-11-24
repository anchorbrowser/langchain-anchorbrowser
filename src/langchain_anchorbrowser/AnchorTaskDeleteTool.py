import json

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from .AnchorBaseTool import AnchorBaseTool, response_payload


class AnchorTaskDeleteTool(AnchorBaseTool, BaseTool):
    name: str = "delete_task"
    description: str = "Delete a task by its ID."
    client_function_name: str = None

    class TaskDeleteInputSchema(BaseModel):
        task_id: str = Field(description="The ID of the task to delete - required")

    args_schema: type[BaseModel] = TaskDeleteInputSchema

    def _run(self, **kwargs) -> str:
        task_id = kwargs["task_id"]
        result = self.client.tasks_legacy.delete_task(task_id)

        data = response_payload(result) or {"success": True, "task_id": task_id}
        return json.dumps(data, indent=2, default=str)
