from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import ClassVar, Optional, Literal


class AnchorContentTool(AnchorBaseTool, BaseTool):
    name: str = "anchor_content_tool"
    description: str = "Get the text content of a webpage using Anchor Browser"
    client_function_name: str = "fetch_webpage"
    needs_session: ClassVar[bool] = False

    class InputSchema(BaseModel):
        url: str = Field(description="The URL of the webpage to get content from")
        format: Optional[Literal['markdown', 'html']] = Field(
            default='markdown',
            description="Preferred content format. Currently always returns markdown.",
        )

    args_schema: type[BaseModel] = InputSchema

    def _run(self, url: str, format: Optional[str] = "markdown", **kwargs) -> str:
        """Fetch webpage content. The format parameter is accepted for compatibility
        but the API always returns markdown-formatted text."""
        return self.client.tools.fetch_webpage(url=url)
