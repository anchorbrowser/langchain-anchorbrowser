
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from .AnchorBaseTool import AnchorBaseTool


class AnchorScreenshotTool(AnchorBaseTool, BaseTool):
    """Screenshot a webpage. Returns the image bytes (PNG or JPEG) as a base64 string."""

    name: str = "anchor_screenshot_tool"
    description: str = "Take a screenshot of a webpage using Anchor Browser. Returns the image as a base64-encoded string."
    client_function_name: str = "screenshot_webpage"

    class InputSchema(BaseModel):
        url: str = Field(description="The URL of the webpage to screenshot")
        width: int | None = Field(default=None, description="Width of the screenshot")
        height: int | None = Field(default=None, description="Height of the screenshot")
        image_quality: int | None = Field(default=None, description="Image quality (1-100)")
        wait: int | None = Field(default=None, description="Wait time in milliseconds")
        scroll_all_content: bool | None = Field(default=None, description="Whether to scroll all content")
        capture_full_height: bool | None = Field(default=None, description="Whether to capture full height")
        s3_target_address: str | None = Field(default=None, description="S3 target address for saving")
    
    args_schema: type[BaseModel] = InputSchema
