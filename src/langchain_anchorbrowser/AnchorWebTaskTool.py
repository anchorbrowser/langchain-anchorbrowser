from langchain_core.tools import BaseTool, BaseToolkit
from pydantic import BaseModel, Field

from .AnchorBaseTool import AnchorBaseTool


class SimpleAnchorWebTaskTool(AnchorBaseTool, BaseTool):
    name: str = "simple_anchor_web_task_tool"
    description: str = "Perform a simple web task using Anchor Browser AI"
    client_function_name: str = "perform_web_task"

    class SimpleWebTaskInputSchema(BaseModel):
        prompt: str = Field(description="The task prompt to execute")
        url: str | None = Field(default=None, description="Starting URL for the task (default: https://example.com)")
    args_schema: type[BaseModel] = SimpleWebTaskInputSchema


class StandardAnchorWebTaskTool(AnchorBaseTool, BaseTool):
    name: str = "standard_anchor_web_task_tool"
    description: str = "Perform a web task using Anchor Browser AI with standard configuration options (agent, provider, model)"
    client_function_name: str = "perform_web_task"

    class StandardWebTaskInputSchema(BaseModel):
        prompt: str = Field(description="The task prompt to execute")
        url: str | None = Field(default=None, description="Starting URL for the task (default: https://example.com)")
        agent: str | None = Field(default=None, description="The AI agent to use (browser-use, openai-cua, or gemini-computer-use, default: browser-use)")
        provider: str | None = Field(default=None, description="The AI provider to use (openai, gemini, groq, azure, xai)")
        model: str | None = Field(default=None, description="The specific model to use for task completion")

    args_schema: type[BaseModel] = StandardWebTaskInputSchema


class AdvancedAnchorWebTaskTool(AnchorBaseTool, BaseTool):
    name: str = "advanced_anchor_web_task_tool"
    description: str = "Perform an advanced web task using Anchor Browser AI"
    client_function_name: str = "perform_web_task"

    class AdvancedWebTaskInputSchema(BaseModel):
        prompt: str = Field(description="The task prompt to execute")
        url: str | None = Field(default=None, description="Starting URL for the task (default: https://example.com)")
        output_schema: dict | None = Field(default=None, description="Output schema for structured results")

    args_schema: type[BaseModel] = AdvancedWebTaskInputSchema

class AnchorWebTaskToolKit(BaseToolkit):
    name: str = "anchor_web_task_tool_kit"
    description: str = "Perform a web task using Anchor Browser AI"

    def get_tools(self) -> list[BaseTool]:
        return [
            SimpleAnchorWebTaskTool(),
            StandardAnchorWebTaskTool(),
            AdvancedAnchorWebTaskTool(),
        ]
