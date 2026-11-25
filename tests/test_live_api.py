"""Live smoke tests against the real Anchor Browser API. Any error fails the test."""

import base64
import json
import os
import unittest
from unittest.mock import patch

from langchain_anchorbrowser import AnchorContentTool, AnchorScreenshotTool, AnchorTaskListTool, SimpleAnchorWebTaskTool
from langchain_anchorbrowser.AnchorBaseTool import AnchorClient


@unittest.skipUnless(os.environ.get("ANCHORBROWSER_API_KEY"), "ANCHORBROWSER_API_KEY not set")
class TestLiveAnchorAPI(unittest.TestCase):
    def setUp(self):
        AnchorClient._instance = None

    def invoke_and_check_session_closed(self, tool, tool_input):
        sessions = tool.client.sessions
        with patch.object(sessions, "delete_session", wraps=sessions.delete_session) as delete_session, \
                self.assertNoLogs("langchain_anchorbrowser", level="WARNING"):
            result = tool.invoke(tool_input)
        delete_session.assert_called_once()
        return result

    def test_content_returns_html(self):
        html = AnchorContentTool().invoke({"url": "https://example.com"})

        self.assertIsInstance(html, str)
        self.assertIn("Example Domain", html)

    def test_screenshot_returns_base64_image(self):
        encoded = self.invoke_and_check_session_closed(
            AnchorScreenshotTool(), {"url": "https://example.com", "width": 800, "height": 600})

        image = base64.b64decode(encoded, validate=True)
        self.assertGreater(len(image), 1000)
        self.assertTrue(image.startswith((b"\xff\xd8\xff", b"\x89PNG")), "expected JPEG or PNG bytes")

    def test_web_task_returns_result(self):
        result = self.invoke_and_check_session_closed(
            SimpleAnchorWebTaskTool(),
            {"prompt": "What is the main heading on this page? Reply with the heading text.", "url": "https://example.com"},
        )

        payload = json.loads(result)
        self.assertTrue(payload)
        self.assertIn("example domain", json.dumps(payload).lower())

    def test_list_tasks_returns_payload(self):
        payload = json.loads(AnchorTaskListTool().invoke({"page": "1", "limit": "5"}))

        self.assertIn("tasks", payload)
        self.assertIsInstance(payload["tasks"], list)
        self.assertIn("total", payload)


if __name__ == '__main__':
    unittest.main()
