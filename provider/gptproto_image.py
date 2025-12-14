from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider
import requests


class GptprotoImageProvider(ToolProvider):
    """GPTProto Image Generation Provider"""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证用户提供的 API Key 是否有效
        """
        api_key = credentials.get("api_key", "")

        if not api_key:
            raise ToolProviderCredentialValidationError("API Key is required")

        # API Key 有效性将在实际调用时验证
