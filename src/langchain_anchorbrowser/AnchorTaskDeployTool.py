from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import Optional
import httpx
import json

class AnchorTaskDeployTool(AnchorBaseTool, BaseTool):
    name: str = "deploy_task"
    description: str = "Deploy a task version. Creates a new version of the task with the provided code, language, and description."
    client_function_name: str = None
    
    class TaskDeployInputSchema(BaseModel):
        task_id: str = Field(description="The ID of the task to deploy - required")
        code: Optional[str] = Field(default=None, description="Base64 encoded task code (required for new versions)")
        language: Optional[str] = Field(default="typescript", description="Programming language for the task (default: 'typescript')")
        description: Optional[str] = Field(default=None, description="Optional description of the version")
    
    args_schema: type[BaseModel] = TaskDeployInputSchema

    def _run(self, **kwargs) -> str:
        """Deploy a task version via HTTP API"""
        task_id = kwargs.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        # Build request body
        body = {}
        if kwargs.get("code"):
            body["code"] = kwargs["code"]
        if kwargs.get("language"):
            body["language"] = kwargs["language"]
        if kwargs.get("description"):
            body["description"] = kwargs["description"]
        
        # Get API key and base URL
        api_key = self.api_key.get_secret_value() if hasattr(self.api_key, 'get_secret_value') else str(self.api_key)
        base_url = str(self.client._client._base_url).rstrip('/')
        url = f"{base_url}/v1/task/{task_id}/deploy"
        
        with httpx.Client() as client:
            response = client.post(
                url,
                headers={
                    "anchor-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json=body,
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)

