from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
import httpx
import json

class AnchorTaskDeleteTool(AnchorBaseTool, BaseTool):
    name: str = "delete_task"
    description: str = "Delete a task by its ID."
    client_function_name: str = None
    
    class TaskDeleteInputSchema(BaseModel):
        task_id: str = Field(description="The ID of the task to delete - required")
    
    args_schema: type[BaseModel] = TaskDeleteInputSchema

    def _run(self, **kwargs) -> str:
        """Delete a task via HTTP API"""
        task_id = kwargs.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        # Get API key and base URL
        api_key = self.api_key.get_secret_value() if hasattr(self.api_key, 'get_secret_value') else str(self.api_key)
        base_url = str(self.client._client._base_url).rstrip('/')
        url = f"{base_url}/v1/task/{task_id}"
        
        with httpx.Client() as client:
            response = client.delete(
                url,
                headers={
                    "anchor-api-key": api_key,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            return json.dumps({"success": True, "task_id": task_id}, indent=2)

