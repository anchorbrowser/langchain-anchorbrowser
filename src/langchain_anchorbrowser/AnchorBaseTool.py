import base64
import getpass
import json
import logging
import os
import time
from typing import Any, ClassVar

from anchorbrowser import Anchorbrowser
from pydantic import SecretStr


class AnchorClient:
    """Singleton class to ensure only one Anchor Browser client instance exists"""
    _instance = None
    _client = None
    _api_key = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self):
        """Initialize API key and client only once"""
        if self._api_key is None:
            env_api_key = os.getenv('ANCHORBROWSER_API_KEY')

            if env_api_key:
                self._api_key = SecretStr(env_api_key)
            else:
                self._api_key = SecretStr(getpass.getpass("Enter API key for Anchor Browser: "))

            self._client = Anchorbrowser(api_key=self._api_key.get_secret_value())
        return self._api_key, self._client


def response_payload(response: Any) -> Any:
    """Return the JSON payload of an anchorbrowser SDK response.

    Several legacy task endpoints return their payload at the top level instead
    of under ``data``; the SDK models keep those keys as extra fields.
    Empty responses (e.g. HTTP 204) come back as ``""`` and yield ``{}``.
    The SDK builds models without validation, so typed fields (UUIDs, datetimes)
    still hold raw strings; serializer warnings about that are suppressed.
    """
    data = getattr(response, "data", None)
    if data is not None:
        return data.model_dump(warnings=False)
    if hasattr(response, "model_dump"):
        return response.model_dump(exclude={"data"}, warnings=False)
    return {}


class AnchorBaseTool:
    """Base class for Anchor Browser tools.

    Provides shared client initialization and a default _run implementation
    that creates a browser session, invokes the requested tool function and
    closes the session again.

    Class attributes:
        client_function_name: Name of the method on ``client.tools`` to call.
        needs_session: Set to False on tools whose underlying API endpoint
            does not accept a ``session_id`` (e.g. ``fetch_webpage``).
    """
    _anchor_api_key: SecretStr | None = None
    _anchor_client: Anchorbrowser | None = None
    _anchor_logger: logging.Logger | None = None

    needs_session: ClassVar[bool] = True

    @property
    def api_key(self) -> SecretStr:
        if self._anchor_api_key is None:
            self._anchor_api_key, _ = AnchorClient().initialize()
        return self._anchor_api_key

    @property
    def client(self) -> Anchorbrowser:
        if self._anchor_client is None:
            _, self._anchor_client = AnchorClient().initialize()
        return self._anchor_client

    @property
    def logger(self) -> logging.Logger:
        if self._anchor_logger is None:
            self._anchor_logger = logging.getLogger(__name__)
        return self._anchor_logger

    def _run(self, **kwargs) -> str:
        """Call the configured tool function inside a short-lived browser session."""
        function_name = self.client_function_name
        if not function_name:
            raise ValueError(f"client_function_name not set for {self.__class__.__name__}")

        request_body = {k: v for k, v in kwargs.items() if v is not None}
        if function_name == "perform_web_task" and "url" not in request_body:
            request_body["url"] = "https://example.com"
            request_body["prompt"] += ". Ignore the starting url."

        start_time = time.time()
        session_id = None
        if self.needs_session:
            session = self.client.sessions.create_session()
            # session.data also carries cdp_url, a credential-bearing websocket URL: never log it.
            session_id = session.data.id if session.data else None
            if session_id:
                request_body["session_id"] = session_id
                self.logger.info("Created Anchor session %s", session_id)

        try:
            client_func = getattr(self.client.tools, function_name)
            result = client_func(**request_body)
        finally:
            if session_id:
                self._close_session(session_id)

        self.logger.info("%s completed in %.2fs", function_name, time.time() - start_time)

        if function_name == "screenshot_webpage":
            return base64.b64encode(result.read()).decode("ascii")
        elif function_name == "perform_web_task":
            # result.data is PerformWebTaskSyncResponseData or PerformWebTaskAsyncResponseData
            if result.data is None:
                return ""
            if hasattr(result.data, "result"):
                return json.dumps(result.data.result, default=str)
            return json.dumps(result.data.model_dump(), default=str)
        else:
            return result

    def _close_session(self, session_id: str) -> None:
        try:
            self.client.sessions.delete_session(session_id)
            self.logger.info("Closed Anchor session %s", session_id)
        except Exception:
            self.logger.warning("Failed to close Anchor session %s", session_id, exc_info=True)
