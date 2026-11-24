from pydantic import SecretStr
from typing import ClassVar
import logging
from anchorbrowser import Anchorbrowser
import getpass
import time
import os
import json


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


class AnchorBaseTool:
    """Base class for Anchor Browser tools.

    Provides shared client initialization and a default _run implementation
    that creates a browser session before invoking the requested tool function.

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
        """Call the configured tool function, optionally pre-creating a session."""
        start_time = time.time()

        request_body = {k: v for k, v in kwargs.items() if v is not None}

        function_name = self.client_function_name
        if not function_name:
            raise ValueError(f"client_function_name not set for {self.__class__.__name__}")

        if self.needs_session:
            if function_name == "perform_web_task" and "url" not in request_body:
                request_body["url"] = "https://example.com"
                request_body["prompt"] += ". Ignore the starting url."

            session = self.client.sessions.create_session()
            live_view_url = session.data.live_view_url if session.data else None
            self.logger.info(f"Session Information: {session.data}")
            if live_view_url:
                self.logger.info(f"Live view URL: {live_view_url}")
            request_body["session_id"] = session.data.id if session.data else None

        client_func = getattr(self.client.tools, function_name)
        self.logger.info(f"Calling {function_name} for: {kwargs.get('url', '')}")
        result = client_func(**request_body)

        execution_time = time.time() - start_time
        self.logger.info(f"{function_name} completed in {execution_time:.2f}s")

        if function_name == "screenshot_webpage":
            return result.text()
        elif function_name == "perform_web_task":
            # result.data is PerformWebTaskSyncResponseData or PerformWebTaskAsyncResponseData
            if result.data is None:
                return ""
            if hasattr(result.data, "result"):
                # Sync response: .result is dict[str, Any]
                return json.dumps(result.data.result)
            # Async response: return workflow_id and status
            return json.dumps(result.data.model_dump())
        else:
            return result
