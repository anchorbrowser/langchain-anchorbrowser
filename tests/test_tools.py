"""Behavior of every tool, observed at the HTTP boundary of a local fake Anchor API."""

import base64
import json
import unittest

from anchorbrowser import InternalServerError, NotFoundError

from langchain_anchorbrowser import (
    AdvancedAnchorWebTaskTool,
    AnchorContentTool,
    AnchorScreenshotTool,
    AnchorTaskCreateTool,
    AnchorTaskDeleteTool,
    AnchorTaskDeployTool,
    AnchorTaskListExecutionsTool,
    AnchorTaskListTool,
    AnchorTaskRunTool,
    AnchorTaskToolKit,
    AnchorWebTaskToolKit,
    SimpleAnchorWebTaskTool,
    StandardAnchorWebTaskTool,
)
from tests.fake_anchor_api import API_KEY, CDP_URL, LIVE_VIEW_URL, SESSION_ID, AnchorAPITestCase

JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + bytes(range(256))
HTML = "<html><body><h1>Example Domain</h1></body></html>"
TASK_ID = "0b5f3c7e-2d4a-4f0e-9a51-3f1c2b7d9e10"


class TestContentTool(AnchorAPITestCase):
    def setUp(self):
        super().setUp()
        self.api.route("POST", "/v1/tools/fetch/webpage", body=HTML.encode(), content_type="text/html")

    def test_returns_html_without_opening_a_session(self):
        result = AnchorContentTool().invoke({"url": "https://example.com"})

        self.assertEqual(result, HTML)
        self.assertEqual(self.api.calls("POST", "/v1/tools/fetch/webpage")[0].json(), {"url": "https://example.com"})
        self.assertEqual(self.api.calls("POST", "/v1/sessions"), [])

    def test_sends_the_api_key_from_the_environment(self):
        AnchorContentTool().invoke({"url": "https://example.com"})

        self.assertEqual(self.api.requests[0].headers["anchor-api-key"], API_KEY)

    def test_legacy_format_argument_is_ignored(self):
        result = AnchorContentTool().invoke({"url": "https://example.com", "format": "markdown"})

        self.assertEqual(result, HTML)
        self.assertEqual(self.api.calls("POST", "/v1/tools/fetch/webpage")[0].json(), {"url": "https://example.com"})


class TestScreenshotTool(AnchorAPITestCase):
    def test_returns_the_image_as_base64_and_closes_the_session(self):
        self.api.route("POST", "/v1/tools/screenshot", body=JPEG, content_type="image/jpeg")

        result = AnchorScreenshotTool().invoke({"url": "https://example.com", "width": 800})

        self.assertEqual(base64.b64decode(result, validate=True), JPEG)
        request = self.api.calls("POST", "/v1/tools/screenshot")[0]
        self.assertEqual(request.query, {"sessionId": SESSION_ID})
        self.assertEqual(request.json(), {"url": "https://example.com", "width": 800})
        self.assertSessionOpenedAndClosed()

    def test_closes_the_session_when_the_screenshot_fails(self):
        self.api.route_json("POST", "/v1/tools/screenshot", {"error": {"code": 500, "message": "failed"}}, status=500)

        with self.assertRaises(InternalServerError):
            AnchorScreenshotTool().invoke({"url": "https://example.com"})

        self.assertSessionOpenedAndClosed()

    def test_failure_to_close_the_session_does_not_hide_the_result(self):
        self.api.route("POST", "/v1/tools/screenshot", body=JPEG, content_type="image/jpeg")
        self.api.route_json("DELETE", f"/v1/sessions/{SESSION_ID}", {"error": {"code": 500}}, status=500)

        with self.assertLogs("langchain_anchorbrowser", level="WARNING") as logs:
            result = AnchorScreenshotTool().invoke({"url": "https://example.com"})

        self.assertEqual(base64.b64decode(result), JPEG)
        self.assertIn(SESSION_ID, "\n".join(logs.output))

    def test_logs_the_session_id_but_never_connection_urls(self):
        self.api.route("POST", "/v1/tools/screenshot", body=JPEG, content_type="image/jpeg")

        with self.assertLogs("langchain_anchorbrowser", level="DEBUG") as logs:
            AnchorScreenshotTool().invoke({"url": "https://example.com"})

        output = "\n".join(logs.output)
        self.assertIn(SESSION_ID, output)
        self.assertNotIn(CDP_URL, output)
        self.assertNotIn(LIVE_VIEW_URL, output)


class TestWebTaskTools(AnchorAPITestCase):
    def setUp(self):
        super().setUp()
        self.api.route_json("POST", "/v1/tools/perform-web-task", {"data": {"result": {"answer": "Example Domain"}}})

    def sent_body(self):
        request = self.api.calls("POST", "/v1/tools/perform-web-task")[0]
        self.assertEqual(request.query, {"sessionId": SESSION_ID})
        return request.json()

    def test_simple_task_returns_the_result_and_closes_the_session(self):
        result = SimpleAnchorWebTaskTool().invoke({"prompt": "Read the heading", "url": "https://example.com"})

        self.assertEqual(json.loads(result), {"answer": "Example Domain"})
        self.assertEqual(self.sent_body(), {"prompt": "Read the heading", "url": "https://example.com"})
        self.assertSessionOpenedAndClosed()

    def test_result_keeps_non_ascii_text(self):
        self.api.route_json("POST", "/v1/tools/perform-web-task", {"data": {"result": {"answer": "東京は晴れ, 21°C"}}})

        result = SimpleAnchorWebTaskTool().invoke({"prompt": "Weather in Tokyo?", "url": "https://example.com"})

        self.assertEqual(result, '{"answer": "東京は晴れ, 21°C"}')

    def test_task_without_url_starts_from_example_com(self):
        SimpleAnchorWebTaskTool().invoke({"prompt": "What is the weather in Tokyo?"})

        self.assertEqual(self.sent_body(), {
            "prompt": "What is the weather in Tokyo?. Ignore the starting url.",
            "url": "https://example.com",
        })

    def test_standard_task_sends_agent_provider_and_model(self):
        StandardAnchorWebTaskTool().invoke({
            "prompt": "Read the heading", "agent": "openai-cua", "provider": "openai", "model": "gpt-4o",
        })

        body = self.sent_body()
        self.assertEqual((body["agent"], body["provider"], body["model"]), ("openai-cua", "openai", "gpt-4o"))

    def test_standard_task_without_options_sends_only_prompt_and_url(self):
        StandardAnchorWebTaskTool().invoke({"prompt": "Read the heading", "url": "https://example.com"})

        self.assertEqual(self.sent_body(), {"prompt": "Read the heading", "url": "https://example.com"})

    def test_advanced_task_sends_the_output_schema(self):
        schema = {"type": "object", "properties": {"heading": {"type": "string"}}}

        AdvancedAnchorWebTaskTool().invoke({"prompt": "Read the heading", "output_schema": schema})

        self.assertEqual(self.sent_body()["output_schema"], schema)

    def test_advanced_task_without_output_schema_sends_none(self):
        AdvancedAnchorWebTaskTool().invoke({"prompt": "Read the heading", "url": "https://example.com"})

        self.assertEqual(self.sent_body(), {"prompt": "Read the heading", "url": "https://example.com"})


class TestTaskTools(AnchorAPITestCase):
    def test_list_tasks_returns_the_top_level_payload(self):
        payload = {"tasks": [{"id": TASK_ID, "name": "demo", "deleted": False}], "total": 1, "page": 2, "limit": 5}
        self.api.route_json("GET", "/v1/task", payload)

        result = json.loads(AnchorTaskListTool().invoke({"page": "2", "limit": "5"}))

        self.assertEqual(result, payload)
        self.assertEqual(self.api.calls("GET", "/v1/task")[0].query, {"page": "2", "limit": "5"})

    def test_list_tasks_defaults_to_the_first_page_of_ten(self):
        self.api.route_json("GET", "/v1/task", {"tasks": [], "total": 0, "page": 1, "limit": 10})

        AnchorTaskListTool().invoke({})

        self.assertEqual(self.api.calls("GET", "/v1/task")[0].query, {"page": "1", "limit": "10"})

    def test_list_executions_returns_the_top_level_payload_and_sends_filters(self):
        payload = {
            "results": [{"id": "exec-1", "status": "success"}],
            "pagination": {"page": 1, "limit": 10, "total": 1, "totalPages": 1},
        }
        self.api.route_json("GET", f"/v1/task/{TASK_ID}/executions", payload)

        result = json.loads(AnchorTaskListExecutionsTool().invoke(
            {"task_id": TASK_ID, "status": "success", "version": "2"}))

        self.assertEqual(result, payload)
        self.assertEqual(self.api.calls("GET", f"/v1/task/{TASK_ID}/executions")[0].query,
                         {"page": "1", "limit": "10", "status": "success", "version": "2"})

    def test_list_executions_skips_blank_filters(self):
        self.api.route_json("GET", f"/v1/task/{TASK_ID}/executions", {"results": [], "pagination": {}})

        AnchorTaskListExecutionsTool().invoke({"task_id": TASK_ID, "status": " ", "version": ""})

        self.assertEqual(self.api.calls("GET", f"/v1/task/{TASK_ID}/executions")[0].query,
                         {"page": "1", "limit": "10"})

    def test_create_task_sends_the_task_and_returns_the_response_body(self):
        task = {"id": TASK_ID, "name": "demo", "language": "typescript", "latestVersion": "draft",
                "createdAt": "2026-01-01T00:00:00Z"}
        self.api.route_json("POST", "/v1/task", {"data": task})

        result = json.loads(AnchorTaskCreateTool().invoke(
            {"name": "demo", "description": "A demo", "code": "ZXhwb3J0IHt9"}))

        self.assertEqual(result, {"data": task})
        self.assertEqual(self.api.calls("POST", "/v1/task")[0].json(),
                         {"name": "demo", "description": "A demo", "code": "ZXhwb3J0IHt9", "language": "typescript"})

    def test_run_task_sends_parsed_inputs(self):
        run = {"success": True, "taskId": TASK_ID, "async": False, "executionTime": 1234, "output": "done"}
        self.api.route_json("POST", "/v1/task/run", {"data": run})

        result = json.loads(AnchorTaskRunTool().invoke(
            {"task_id": TASK_ID, "version": "1", "inputs": '{"ANCHOR_TARGET_URL": "https://example.com"}'}))

        self.assertEqual(result, {"data": run})
        self.assertEqual(self.api.calls("POST", "/v1/task/run")[0].json(), {
            "taskId": TASK_ID, "version": "1", "inputs": {"ANCHOR_TARGET_URL": "https://example.com"},
        })

    def test_task_responses_keep_non_ascii_text(self):
        self.api.route_json("POST", "/v1/task/run", {"data": {"success": True, "output": "café"}})

        result = AnchorTaskRunTool().invoke({"task_id": TASK_ID})

        self.assertIn('"output": "café"', result)

    def test_run_task_rejects_invalid_inputs_without_calling_the_api(self):
        with self.assertRaises(ValueError):
            AnchorTaskRunTool().invoke({"task_id": TASK_ID, "inputs": "{not json"})

        self.assertEqual(self.api.requests, [])

    def test_deploy_task_sends_the_new_version(self):
        self.api.route_json("POST", f"/v1/task/{TASK_ID}/deploy", {"data": {"id": "ver-1", "version": "1"}})

        result = json.loads(AnchorTaskDeployTool().invoke(
            {"task_id": TASK_ID, "code": "ZXhwb3J0IHt9", "description": "v1"}))

        self.assertEqual(result, {"data": {"id": "ver-1", "version": "1"}})
        self.assertEqual(self.api.calls("POST", f"/v1/task/{TASK_ID}/deploy")[0].json(),
                         {"code": "ZXhwb3J0IHt9", "description": "v1"})

    def test_delete_task_reports_success(self):
        self.api.route_json("DELETE", f"/v1/task/{TASK_ID}", {"data": {"message": "Task deleted successfully"}})

        result = json.loads(AnchorTaskDeleteTool().invoke({"task_id": TASK_ID}))

        self.assertEqual(result, {"success": True, "task_id": TASK_ID})
        self.assertEqual(len(self.api.calls("DELETE", f"/v1/task/{TASK_ID}")), 1)

    def test_delete_task_raises_when_the_task_does_not_exist(self):
        self.api.route_json("DELETE", f"/v1/task/{TASK_ID}", {"error": {"code": 404}}, status=404)

        with self.assertRaises(NotFoundError):
            AnchorTaskDeleteTool().invoke({"task_id": TASK_ID})


class TestToolkits(unittest.TestCase):
    def test_toolkits_bundle_their_tools(self):
        self.assertEqual([t.name for t in AnchorWebTaskToolKit().get_tools()],
                         ["simple_anchor_web_task_tool", "standard_anchor_web_task_tool",
                          "advanced_anchor_web_task_tool"])
        self.assertEqual([t.name for t in AnchorTaskToolKit().get_tools()],
                         ["create_task", "list_tasks", "delete_task", "run_task", "deploy_task",
                          "list_task_executions"])


if __name__ == '__main__':
    unittest.main()
