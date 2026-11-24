from .AnchorBaseTool import AnchorBaseTool
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import ClassVar


class AnchorContentTool(AnchorBaseTool, BaseTool):
    """Fetch a webpage through Anchor's Web Unlocker.

    Returns the fully rendered HTML of the page. The endpoint has no format
    option, so the content is always HTML (or the upstream body for non-HTML
    resources such as JSON or plain text).
    """

    name: str = "anchor_content_tool"
    description: str = "Get the fully rendered HTML of a webpage using Anchor Browser"
    client_function_name: str = "fetch_webpage"
    needs_session: ClassVar[bool] = False

    class InputSchema(BaseModel):
        url: str = Field(description="The URL of the webpage to get content from")

    args_schema: type[BaseModel] = InputSchema

    def _run(self, url: str, **kwargs) -> str:
        return self.client.tools.fetch_webpage(url=url)
