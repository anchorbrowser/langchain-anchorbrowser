import json

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from .AnchorBaseTool import AnchorBaseTool, response_payload


class AnchorTaskDeployTool(AnchorBaseTool, BaseTool):
    name: str = "deploy_task"
    description: str = "Deploy a task version. Creates a new version of the task with the provided code, language, and description."
    client_function_name: str = None

    class TaskDeployInputSchema(BaseModel):
        task_id: str = Field(description="The ID of the task to deploy - required")
        code: str | None = Field(default=None, description="Base64 encoded task code (required for new versions)")
        language: str | None = Field(default="typescript", description="Programming language for the task (default: 'typescript')")
        description: str | None = Field(default=None, description="Optional description of the version")

    args_schema: type[BaseModel] = TaskDeployInputSchema

    def _run(self, **kwargs) -> str:
        task_id = kwargs.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")

        deploy_kwargs = {"task_id": task_id}
        if kwargs.get("code"):
            deploy_kwargs["code"] = kwargs["code"]
        if kwargs.get("language"):
            deploy_kwargs["language"] = kwargs["language"]
        if kwargs.get("description"):
            deploy_kwargs["description"] = kwargs["description"]

        result = self.client.tasks_legacy.deploy_task(**deploy_kwargs)

        data = response_payload(result)
        return json.dumps(data, indent=2, default=str)
