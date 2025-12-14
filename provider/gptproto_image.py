from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider


class GptprotoImageProvider(ToolProvider):
    """GPTProto Image Generation Provider"""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证用户提供的 API Key 是否有效
        """
        try:
            api_key = credentials.get("api_key", "")

            if not api_key:
                raise ToolProviderCredentialValidationError("API Key is required")

            # 不做额外验证，直接通过
            # API Key 有效性将在实际调用时验证

        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
