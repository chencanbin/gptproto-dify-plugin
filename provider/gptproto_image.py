from typing import Any
from dify_plugin import ToolProvider


class GptprotoImageProvider(ToolProvider):
    """GPTProto Image Generation Provider"""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        无需凭证验证，直接返回成功
        """
        return None
