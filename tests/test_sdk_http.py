"""Run the tools through the real anchorbrowser SDK against a mocked HTTP layer.

Method-level mocks cannot catch mismatches between the SDK's response models
and the payloads the API actually returns; these tests can.
"""

import base64
import json
import os
import sys
import unittest

import httpx
from anchorbrowser import Anchorbrowser, InternalServerError
from pydantic import SecretStr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_anchorbrowser import (
    AdvancedAnchorWebTaskTool,
    AnchorContentTool,
    AnchorScreenshotTool,
    AnchorTaskCreateTool,
    AnchorTaskDeleteTool,
    AnchorTaskListExecutionsTool,
    AnchorTaskListTool,
    SimpleAnchorWebTaskTool,
)
from langchain_anchorbrowser.AnchorBaseTool import AnchorClient

SESSION_ID = "sess-1"
CDP_URL = "wss://connect.anchorbrowser.io?apiKey=not-a-real-key&sessionId=sess-1"
LIVE_VIEW_URL = "https://live.anchorbrowser.io?sessionId=sess-1"
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + bytes(range(256))


class FakeAnchorAPI:
    def __init__(self):
        self.requests = []
        self.routes = {}

    def route(self, method, path, respond):
        self.routes[(method, path)] = respond

    def handler(self, request):
        self.requests.append(request)
        respond = self.routes.get((request.method, request.url.path))
        if respond is None:
            return httpx.Response(404, json={"error": "not found"})
        return respond(request)

    def calls(self, method, path):
        return [r for r in self.requests if r.method == method and r.url.path == path]


class SDKTestCase(unittest.TestCase):
    def setUp(self):
        self.api = FakeAnchorAPI()
        self.api.route("POST", "/v1/sessions", lambda r: httpx.Response(
            200, json={"data": {"id": SESSION_ID, "cdp_url": CDP_URL, "live_view_url": LIVE_VIEW_URL}}))
        self.api.route("DELETE", f"/v1/sessions/{SESSION_ID}", lambda r: httpx.Response(
            200, json={"data": {"status": "deleted"}}))
        client = Anchorbrowser(
            api_key="test-key",
            base_url="https://api.test",
            http_client=httpx.Client(transport=httpx.MockTransport(self.api.handler)),
        )
        AnchorClient._instance = None
        AnchorClient._api_key = SecretStr("test-key")
        AnchorClient._client = client

    def tearDown(self):
        AnchorClient._instance = None
        AnchorClient._api_key = None
        AnchorClient._client = None

    def assertSessionClosed(self):
        self.assertEqual(len(self.api.calls("POST", "/v1/sessions")), 1)
        self.assertEqual(len(self.api.calls("DELETE", f"/v1/sessions/{SESSION_ID}")), 1)


class TestTaskPayloadShapes(SDKTestCase):
    def test_list_tasks_returns_top_level_payload(self):
        payload = {
            "tasks": [{"id": "task-1", "name": "demo", "description": None, "deleted": False}],
            "total": 1,
            "page": 1,
            "limit": 10,
        }
        self.api.route("GET", "/v1/task", lambda r: httpx.Response(200, json=payload))

        result = json.loads(AnchorTaskListTool().invoke({"page": "2", "limit": "10"}))

        self.assertEqual(result, payload)
        request = self.api.calls("GET", "/v1/task")[0]
        self.assertEqual(request.url.params["page"], "2")
        self.assertEqual(request.url.params["limit"], "10")

    def test_list_executions_returns_top_level_payload(self):
        payload = {
            "results": [{"id": "exec-1", "status": "success", "output": "done"}],
            "pagination": {"page": 1, "limit": 10, "total": 1, "totalPages": 1},
        }
        self.api.route("GET", "/v1/task/task-1/executions", lambda r: httpx.Response(200, json=payload))

        result = json.loads(AnchorTaskListExecutionsTool().invoke({"task_id": "task-1", "status": "success"}))

        self.assertEqual(result, payload)
        params = self.api.calls("GET", "/v1/task/task-1/executions")[0].url.params
        self.assertEqual(params["status"], "success")
        self.assertNotIn("version", params)

    def test_payload_wrapped_in_data_is_unwrapped(self):
        task_id = "0b5f3c7e-2d4a-4f0e-9a51-3f1c2b7d9e10"
        self.api.route("POST", "/v1/task", lambda r: httpx.Response(
            200, json={"data": {"id": task_id, "name": "demo", "language": "typescript"}}))

        result = json.loads(AnchorTaskCreateTool().invoke({"name": "demo"}))

        self.assertEqual(result["id"], task_id)
        self.assertEqual(result["name"], "demo")
        self.assertNotIn("data", result)

    def test_delete_task_with_empty_response(self):
        self.api.route("DELETE", "/v1/task/task-1", lambda r: httpx.Response(204))

        result = json.loads(AnchorTaskDeleteTool().invoke({"task_id": "task-1"}))

        self.assertEqual(result, {"success": True, "task_id": "task-1"})


class TestScreenshot(SDKTestCase):
    def test_returns_base64_image_and_closes_session(self):
        self.api.route("POST", "/v1/tools/screenshot", lambda r: httpx.Response(
            200, content=JPEG, headers={"content-type": "image/jpeg"}))

        result = AnchorScreenshotTool().invoke({"url": "https://example.com", "width": 800})

        self.assertEqual(base64.b64decode(result, validate=True), JPEG)
        request = self.api.calls("POST", "/v1/tools/screenshot")[0]
        self.assertEqual(request.url.params["sessionId"], SESSION_ID)
        self.assertEqual(json.loads(request.content), {"url": "https://example.com", "width": 800})
        self.assertSessionClosed()

    def test_session_closed_when_screenshot_fails(self):
        self.api.route("POST", "/v1/tools/screenshot", lambda r: httpx.Response(
            500, json={"error": {"code": 500, "message": "Failed to take screenshot"}}))

        with self.assertRaises(InternalServerError):
            AnchorScreenshotTool().invoke({"url": "https://example.com"})

        self.assertSessionClosed()


class TestWebTask(SDKTestCase):
    def test_returns_result_and_closes_session(self):
        self.api.route("POST", "/v1/tools/perform-web-task", lambda r: httpx.Response(
            200, json={"data": {"result": {"answer": "Example Domain"}}}))

        result = SimpleAnchorWebTaskTool().invoke({"prompt": "Read the heading", "url": "https://example.com"})

        self.assertEqual(json.loads(result), {"answer": "Example Domain"})
        self.assertSessionClosed()

    def test_task_without_url_starts_from_example_com(self):
        self.api.route("POST", "/v1/tools/perform-web-task", lambda r: httpx.Response(
            200, json={"data": {"result": {"answer": "sunny"}}}))

        SimpleAnchorWebTaskTool().invoke({"prompt": "What is the weather in Tokyo?"})

        self.assertEqual(json.loads(self.api.calls("POST", "/v1/tools/perform-web-task")[0].content), {
            "url": "https://example.com",
            "prompt": "What is the weather in Tokyo?. Ignore the starting url.",
        })

    def test_advanced_task_without_output_schema_sends_none(self):
        self.api.route("POST", "/v1/tools/perform-web-task", lambda r: httpx.Response(
            200, json={"data": {"result": {"answer": "sunny"}}}))

        AdvancedAnchorWebTaskTool().invoke({"prompt": "Read the heading", "url": "https://example.com"})

        self.assertNotIn("output_schema", json.loads(self.api.calls("POST", "/v1/tools/perform-web-task")[0].content))


class TestContent(SDKTestCase):
    def test_returns_html_without_creating_a_session(self):
        html = "<html><body><h1>Example Domain</h1></body></html>"
        self.api.route("POST", "/v1/tools/fetch/webpage", lambda r: httpx.Response(
            200, text=html, headers={"content-type": "text/html"}))

        result = AnchorContentTool().invoke({"url": "https://example.com"})

        self.assertEqual(result, html)
        request = self.api.calls("POST", "/v1/tools/fetch/webpage")[0]
        self.assertEqual(json.loads(request.content), {"url": "https://example.com"})
        self.assertEqual(self.api.calls("POST", "/v1/sessions"), [])


class TestLogging(SDKTestCase):
    def test_logs_session_id_but_never_connection_urls(self):
        self.api.route("POST", "/v1/tools/screenshot", lambda r: httpx.Response(
            200, content=JPEG, headers={"content-type": "image/jpeg"}))

        with self.assertLogs("langchain_anchorbrowser", level="DEBUG") as logs:
            AnchorScreenshotTool().invoke({"url": "https://example.com"})

        output = "\n".join(logs.output)
        self.assertIn(SESSION_ID, output)
        self.assertNotIn(CDP_URL, output)
        self.assertNotIn("wss://", output)
        self.assertNotIn(LIVE_VIEW_URL, output)


if __name__ == '__main__':
    unittest.main()
