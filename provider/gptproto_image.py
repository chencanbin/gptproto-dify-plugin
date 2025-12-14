from typing import Any
import requests
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider


class GptprotoImageProvider(ToolProvider):
    """GPTProto Image Generation Provider"""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证用户提供的 API Key 是否有效
        通过调用 GPTProto API 验证凭证
        """
        api_key = credentials.get("api_key", "")

        if not api_key:
            raise ToolProviderCredentialValidationError("API Key is required")

        # 调用 API 验证 Key 是否有效
        try:
            response = requests.get(
                "https://gptproto.com/api/v3/user/me",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )

            if response.status_code == 401:
                raise ToolProviderCredentialValidationError(
                    "Invalid API Key. Please check your GPTProto API Key."
                )
            elif response.status_code == 403:
                raise ToolProviderCredentialValidationError(
                    "API Key does not have permission to access this service."
                )
            elif not response.ok:
                raise ToolProviderCredentialValidationError(
                    f"Failed to validate API Key: HTTP {response.status_code}"
                )

        except requests.Timeout:
            raise ToolProviderCredentialValidationError(
                "Connection timeout. Please check your network and try again."
            )
        except requests.ConnectionError:
            raise ToolProviderCredentialValidationError(
                "Cannot connect to GPTProto server. Please check your network."
            )
        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Validation error: {str(e)}")
