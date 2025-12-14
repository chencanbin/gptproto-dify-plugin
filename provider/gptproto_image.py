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

        if not api_key.startswith("sk-"):
            raise ToolProviderCredentialValidationError(
                'Invalid API Key format. Must start with "sk-"'
            )

        # 简单验证 API Key 格式即可，实际调用时会验证有效性
        # 这里不做实际 API 调用，避免不必要的请求
