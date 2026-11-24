"""A local stand-in for the Anchor API.

The tools run unmodified: they build the real anchorbrowser SDK client from
ANCHORBROWSER_API_KEY and ANCHORBROWSER_BASE_URL, and the SDK talks HTTP to this server.
Tests assert on the requests the server received and on what the tools return.
"""

import json
import os
import threading
import unittest
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from urllib.parse import parse_qsl, urlsplit

from langchain_anchorbrowser.AnchorBaseTool import AnchorClient

API_KEY = "test-api-key"
SESSION_ID = "sess-1"
CDP_URL = "wss://connect.anchorbrowser.io?apiKey=not-a-real-key&sessionId=sess-1"
LIVE_VIEW_URL = "https://live.anchorbrowser.io?sessionId=sess-1"


@dataclass
class Request:
    method: str
    path: str
    query: dict
    headers: dict
    body: bytes

    def json(self):
        return json.loads(self.body)


@dataclass
class Response:
    status: int = 200
    body: bytes = b""
    content_type: str = "application/json"


class FakeAnchorAPI:
    def __init__(self):
        self.requests = []
        self.routes = {}
        api = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def handle_request(self):
                url = urlsplit(self.path)
                length = int(self.headers.get("content-length") or 0)
                request = Request(self.command, url.path, dict(parse_qsl(url.query)),
                                  {k.lower(): v for k, v in self.headers.items()}, self.rfile.read(length))
                api.requests.append(request)
                response = api.routes.get((request.method, request.path), Response(404, b'{"error": "not found"}'))
                self.send_response(response.status)
                self.send_header("content-type", response.content_type)
                self.send_header("content-length", str(len(response.body)))
                self.end_headers()
                self.wfile.write(response.body)

            do_GET = do_POST = do_PUT = do_DELETE = handle_request

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def reset(self):
        self.requests = []
        self.routes = {}
        self.route_json("POST", "/v1/sessions",
                        {"data": {"id": SESSION_ID, "cdp_url": CDP_URL, "live_view_url": LIVE_VIEW_URL}})
        self.route_json("DELETE", f"/v1/sessions/{SESSION_ID}", {"data": {"status": "deleted"}})

    def route(self, method, path, status=200, body=b"", content_type="application/json"):
        self.routes[(method, path)] = Response(status, body, content_type)

    def route_json(self, method, path, payload, status=200):
        self.route(method, path, status, json.dumps(payload).encode())

    def calls(self, method, path):
        return [r for r in self.requests if r.method == method and r.path == path]


_api = None


class AnchorAPITestCase(unittest.TestCase):
    def setUp(self):
        global _api
        if _api is None:
            _api = FakeAnchorAPI()
        self.api = _api
        self.api.reset()
        env = patch.dict(os.environ, {"ANCHORBROWSER_API_KEY": API_KEY, "ANCHORBROWSER_BASE_URL": self.api.url})
        env.start()
        self.addCleanup(env.stop)
        # The client is a process-wide singleton; start each test from a fresh one built from the env above.
        AnchorClient._instance = None
        self.addCleanup(setattr, AnchorClient, "_instance", None)

    def assertSessionOpenedAndClosed(self):
        self.assertEqual(len(self.api.calls("POST", "/v1/sessions")), 1)
        self.assertEqual(len(self.api.calls("DELETE", f"/v1/sessions/{SESSION_ID}")), 1)
