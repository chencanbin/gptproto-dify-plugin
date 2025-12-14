from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GptprotoImageProvider(ToolProvider):
    """GPTProto Image Generation Provider"""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证 API Key 是否有效
        """
        api_key = credentials.get("api_key")

        if not api_key:
            raise ToolProviderCredentialValidationError("API Key is required")

        try:
            # 用轻量接口测试 Key 是否有效
            resp = requests.get(
                "https://gptproto.com/api/v3/user/me",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )

            if resp.status_code == 401:
                raise ToolProviderCredentialValidationError("Invalid API Key")

            if resp.status_code == 403:
                raise ToolProviderCredentialValidationError(
                    "API Key has no permission"
                )

            if resp.status_code >= 400:
                raise ToolProviderCredentialValidationError(
                    f"Credential validation failed: {resp.text}"
                )

        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to validate API Key: {str(e)}"
            )
