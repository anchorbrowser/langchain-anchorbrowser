from .AnchorBaseTool import AnchorBaseTool, response_payload
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import Optional
import json


class AnchorTaskCreateTool(AnchorBaseTool, BaseTool):
    name: str = "create_task"
    description: str = "Create a new task or update an existing task with the same name. Tasks are reusable code snippets that can be executed in browser sessions."
    client_function_name: str = None

    class TaskCreateInputSchema(BaseModel):
        name: str = Field(description="Task name (letters, numbers, hyphens, and underscores only) - required")
        description: Optional[str] = Field(default=None, description="Optional description of the task")
        code: Optional[str] = Field(default=None, description="Base64 encoded task code (optional)")
        language: Optional[str] = Field(default="typescript", description="Programming language for the task (default: 'typescript')")

    args_schema: type[BaseModel] = TaskCreateInputSchema

    def _run(self, **kwargs) -> str:
        if not kwargs.get("name"):
            raise ValueError("Task name is required")

        result = self.client.tasks_legacy.create_task(
            name=kwargs["name"],
            language=kwargs.get("language", "typescript"),
            description=kwargs.get("description"),
            code=kwargs.get("code"),
        )

        data = response_payload(result)
        return json.dumps(data, indent=2, default=str)
