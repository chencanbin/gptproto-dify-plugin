from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GptprotoImageProvider(ToolProvider):
    """GPTProto Image Generation Provider"""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证凭证 - 此插件使用内置 API Key，无需验证
        """
        try:
            # 不需要验证，直接通过
            pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
