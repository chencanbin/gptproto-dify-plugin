from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

API_BASE = "https://gptproto.com/v1"


class ClaudeSonnet45TextGenerationTool(Tool):
    """
    Tool for generating text, analyzing documents, and searching the web
    using Anthropic Claude Sonnet 4.5 model via GPTProto API.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invoke the Claude Sonnet 4.5 text generation tool.
        """
        # Get API key from credentials
        api_key = self.runtime.credentials.get("api_key")
        if not api_key:
            yield self.create_text_message("Error: API key is required")
            return

        # Get parameters
        prompt = tool_parameters.get("prompt", "")
        if not prompt:
            yield self.create_text_message("Error: Prompt is required")
            return

        document_url = tool_parameters.get("document_url", "")
        enable_web_search = tool_parameters.get("enable_web_search", False)
        max_tokens = tool_parameters.get("max_tokens", 4096)

        try:
            # Call API directly
            result = self._generate_text(
                api_key=api_key,
                prompt=prompt,
                document_url=document_url,
                enable_web_search=enable_web_search,
                max_tokens=max_tokens,
            )

            if result:
                yield self.create_text_message(result)
            else:
                yield self.create_text_message("Error: Failed to generate text")

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

    def _generate_text(
        self,
        api_key: str,
        prompt: str,
        document_url: str,
        enable_web_search: bool,
        max_tokens: int,
    ) -> str | None:
        """
        Generate text using Claude Sonnet 4.5 API.
        """
        url = f"{API_BASE}/messages"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        # Build content
        if document_url:
            # Multimodal content with document
            content = [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "document",
                    "source": {
                        "type": "url",
                        "url": document_url
                    }
                }
            ]
        else:
            # Simple text content
            content = prompt

        # Build request data
        data = {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }

        # Add web search tool if enabled
        if enable_web_search:
            data["tools"] = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5
                }
            ]

        response = requests.post(url, headers=headers, json=data, timeout=120)

        if response.status_code != 200:
            raise Exception(f"API request failed: HTTP {response.status_code} - {response.text}")

        result = response.json()

        # Extract text from Claude API response
        # Response format: {"content": [{"type": "text", "text": "..."}], ...}
        content_blocks = result.get("content", [])
        if content_blocks:
            text_parts = []
            for block in content_blocks:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            if text_parts:
                return "\n".join(text_parts)

        # Try other common fields
        if "text" in result:
            return result["text"]

        if "message" in result:
            message = result["message"]
            if isinstance(message, str):
                return message
            elif isinstance(message, dict):
                return message.get("content", "")

        # Handle wrapped response
        if "data" in result:
            data_obj = result["data"]
            if isinstance(data_obj, dict):
                return data_obj.get("text") or data_obj.get("content") or data_obj.get("output")

        return None
