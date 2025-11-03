from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import Optional
import json

class AnchorTaskRunTool(AnchorBaseTool, BaseTool):
    name: str = "run_task"
    description: str = "Execute a task in a browser session. The task can be run with a specific version or the latest version. Optionally, you can provide an existing session ID or let the system create a new one."
    client_function_name: str = None
    
    class TaskRunInputSchema(BaseModel):
        task_id: str = Field(description="Task identifier - required")
        version: Optional[str] = Field(default="latest", description="Version to run (draft, latest, or version number, default: 'latest')")
        session_id: Optional[str] = Field(default=None, description="Optional existing session ID to use")
        inputs: Optional[str] = Field(default=None, description="Environment variables for task execution as JSON string (keys must start with ANCHOR_)")
    
    args_schema: type[BaseModel] = TaskRunInputSchema

    def _run(self, **kwargs) -> str:
        """Run a task using the client SDK"""
        task_id = kwargs.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
        
        # Parse inputs if provided
        inputs = None
        if kwargs.get("inputs"):
            try:
                inputs = json.loads(kwargs["inputs"]) if isinstance(kwargs["inputs"], str) else kwargs["inputs"]
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in inputs: {e}")
        
        # Build call arguments, only including optional parameters if they're provided
        call_kwargs = {
            "task_id": task_id,
            "version": kwargs.get("version", "latest"),
        }
        
        # Only add session_id if it's provided and not None
        if kwargs.get("session_id") is not None:
            call_kwargs["session_id"] = kwargs["session_id"]
        
        # Only add inputs if they're provided
        if inputs is not None:
            call_kwargs["inputs"] = inputs
        
        result = self.client.task.run(**call_kwargs)
        
        return json.dumps(result.model_dump(), indent=2, default=str)

