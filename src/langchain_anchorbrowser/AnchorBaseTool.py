from pydantic import SecretStr
import logging
from anchorbrowser import Anchorbrowser
import getpass
import time
import os

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
            print(f"Checking for ANCHORBROWSER_API_KEY env var...")
            env_api_key = os.getenv('ANCHORBROWSER_API_KEY')
            
            if env_api_key:
                # Use environment variable directly
                self._api_key = SecretStr(env_api_key)
                print(f"Using API key from environment variable")
            else:
                # Fall back to prompt
                self._api_key = SecretStr(getpass.getpass("Enter API key for Anchor Browser: "))
                print(f"Using API key from prompt")
            
            self._client = Anchorbrowser(api_key=self._api_key.get_secret_value())
            print(f"Created new API key and client instances")
        return self._api_key, self._client

# Base configuration for all tools
class AnchorBaseTool:
    """Base class for Anchor Browser tools. Provides shared client initialization.
    
    This mixin works with Pydantic v2 by using lazy initialization. The client
    is initialized on first access rather than in __init__.
    
    Note: Subclasses should define client_function_name as a class attribute,
    not as a Pydantic Field, to avoid shadowing warnings.
    """
    _anchor_api_key: SecretStr | None = None
    _anchor_client: Anchorbrowser | None = None
    _anchor_logger: logging.Logger | None = None

    @property
    def api_key(self) -> SecretStr:
        """Get or initialize the API key"""
        if self._anchor_api_key is None:
            self._anchor_api_key, _ = AnchorClient().initialize()
        return self._anchor_api_key
    
    @property
    def client(self) -> Anchorbrowser:
        """Get or initialize the client"""
        if self._anchor_client is None:
            _, self._anchor_client = AnchorClient().initialize()
            print(f"Initialized client for {self.__class__.__name__}")
        return self._anchor_client
    
    @property
    def logger(self) -> logging.Logger:
        """Get or initialize the logger"""
        if self._anchor_logger is None:
            self._anchor_logger = logging.getLogger(__name__)
        return self._anchor_logger

    def _run(self, **kwargs) -> str:
        """Generic run method that calls the appropriate client function"""
        start_time = time.time()
        
        # Filter out None values
        request_body = {k: v for k, v in kwargs.items() if v is not None}

        if self.client_function_name == "perform_web_task" and "url" not in request_body:
            request_body["url"] = "https://example.com"
            request_body["prompt"] += ". Ignore the starting url."

        # Get the function name from the class attribute
        function_name = self.client_function_name
        if not function_name:
            raise ValueError(f"client_function_name not set for {self.__class__.__name__}")
        
        # Create a new session
        session = self.client.sessions.create()
        live_view_url = session.data.live_view_url
        self.logger.info(f"Session Information: {session.data}")
        print(f"Live view URL: {live_view_url}")
        request_body["session_id"] = session.data.id

        # Get the function from the client
        client_func = getattr(self.client.tools, function_name)  
        self.logger.info(f"Calling {function_name} for: {kwargs.get('url', '')}")
        result = client_func(**request_body)
        
        execution_time = time.time() - start_time
        self.logger.info(f"{function_name} completed in {execution_time:.2f}s")
        if function_name == "screenshot_webpage":
            return result.text()
        elif function_name == "perform_web_task":
            return result.data
        else:
            return result
