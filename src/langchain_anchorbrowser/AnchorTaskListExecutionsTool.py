import json

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from .AnchorBaseTool import AnchorBaseTool, response_payload


class AnchorTaskListExecutionsTool(AnchorBaseTool, BaseTool):
    name: str = "list_task_executions"
    description: str = "List task execution results for a specific task. Returns paginated execution results with optional filtering by status and version."
    client_function_name: str = None

    class TaskListExecutionsInputSchema(BaseModel):
        task_id: str = Field(description="The task ID to list executions for - required")
        page: str = Field(default="1", description="Page number (default: 1)")
        limit: str = Field(default="10", description="Number of results per page (default: 10)")
        status: str | None = Field(default=None, description="Filter by execution status (success, failure, timeout, cancelled). Leave empty for all.")
        version: str | None = Field(default=None, description="Filter by task version (draft, latest, or version number). Leave empty for all versions.")

    args_schema: type[BaseModel] = TaskListExecutionsInputSchema

    def _run(self, **kwargs) -> str:
        task_id = kwargs.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")

        list_kwargs = {
            "task_id": task_id,
            "page": kwargs.get("page", "1"),
            "limit": kwargs.get("limit", "10"),
        }

        status = kwargs.get("status")
        if status and status.strip():
            list_kwargs["status"] = status

        version = kwargs.get("version")
        if version and version.strip():
            list_kwargs["version"] = version

        result = self.client.tasks_legacy.list_task_executions(**list_kwargs)

        data = response_payload(result)
        return json.dumps(data, indent=2, default=str)
