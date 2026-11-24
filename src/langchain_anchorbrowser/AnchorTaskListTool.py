import json

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from .AnchorBaseTool import AnchorBaseTool, response_payload


class AnchorTaskListTool(AnchorBaseTool, BaseTool):
    name: str = "list_tasks"
    description: str = "List all tasks for the authenticated team. Returns paginated results with task metadata."
    client_function_name: str = None

    class TaskListInputSchema(BaseModel):
        page: str = Field(default="1", description="Page number (default: 1)")
        limit: str = Field(default="10", description="Number of results per page (default: 10)")

    args_schema: type[BaseModel] = TaskListInputSchema

    def _run(self, **kwargs) -> str:
        result = self.client.tasks_legacy.list_tasks(
            page=kwargs.get("page", "1"),
            limit=kwargs.get("limit", "10"),
        )

        data = response_payload(result)
        return json.dumps(data, indent=2, default=str)
