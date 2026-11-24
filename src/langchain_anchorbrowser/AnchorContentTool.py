from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from .AnchorBaseTool import AnchorBaseTool


class AnchorContentTool(AnchorBaseTool, BaseTool):
    """Fetch a webpage through Anchor's Web Unlocker.

    Returns the fully rendered HTML of the page, or the body of other text
    resources such as JSON or plain text. The endpoint has no format option.
    Binary downloads such as PDFs are not supported: the SDK decodes them as text.
    """

    name: str = "anchor_content_tool"
    description: str = "Get the fully rendered HTML of a webpage using Anchor Browser"

    class InputSchema(BaseModel):
        url: str = Field(description="The URL of the webpage to get content from")

    args_schema: type[BaseModel] = InputSchema

    def _run(self, url: str) -> str:
        return self.client.tools.fetch_webpage(url=url)
