from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import Optional
import httpx
import json

class AnchorTaskListExecutionsTool(AnchorBaseTool, BaseTool):
    name: str = "list_task_executions"
    description: str = "List task execution results for a specific task. Returns paginated execution results with optional filtering by status and version."
    client_function_name: str = None
    
    class TaskListExecutionsInputSchema(BaseModel):
        task_id: str = Field(description="The task ID to list executions for - required")
        page: str = Field(default="1", description="Page number (default: 1)")
        limit: str = Field(default="10", description="Number of results per page (default: 10)")
        status: Optional[str] = Field(default=None, description="Filter by execution status (success, failure, timeout, cancelled). Leave empty for all.")
        version: Optional[str] = Field(default=None, description="Filter by task version (draft, latest, or version number). Leave empty for all versions.")
    
    args_schema: type[BaseModel] = TaskListExecutionsInputSchema

    def _run(self, **kwargs) -> str:
        """List task executions via HTTP API"""
        task_id = kwargs.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        # Build query parameters
        query_params = {
            "page": kwargs.get("page", "1"),
            "limit": kwargs.get("limit", "10"),
        }
        
        # Only add status if provided and not empty
        status = kwargs.get("status")
        if status and status.strip():
            query_params["status"] = status
        
        # Only add version if provided and not empty
        version = kwargs.get("version")
        if version and version.strip():
            query_params["version"] = version
        
        # Get API key and base URL
        api_key = self.api_key.get_secret_value() if hasattr(self.api_key, 'get_secret_value') else str(self.api_key)
        base_url = str(self.client._client._base_url).rstrip('/')
        url = f"{base_url}/v1/task/{task_id}/executions"
        
        with httpx.Client() as client:
            response = client.get(
                url,
                headers={
                    "anchor-api-key": api_key,
                    "Content-Type": "application/json",
                },
                params=query_params,
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)

