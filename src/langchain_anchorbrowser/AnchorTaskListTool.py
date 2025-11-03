from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
import json

class AnchorTaskListTool(AnchorBaseTool, BaseTool):
    name: str = "list_tasks"
    description: str = "List all tasks for the authenticated team. Returns paginated results with task metadata."
    client_function_name: str = None
    
    class TaskListInputSchema(BaseModel):
        page: str = Field(default="1", description="Page number (default: 1)")
        limit: str = Field(default="10", description="Number of results per page (default: 10)")
    
    args_schema: type[BaseModel] = TaskListInputSchema

    def _run(self, **kwargs) -> str:
        """List tasks using the client SDK"""
        result = self.client.task.list(
            page=kwargs.get("page", "1"),
            limit=kwargs.get("limit", "10"),
        )
        
        return json.dumps(result.model_dump(), indent=2, default=str)

