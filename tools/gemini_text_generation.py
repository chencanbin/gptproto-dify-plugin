from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

API_BASE = "https://gptproto.com/v1beta"


class GeminiTextGenerationTool(Tool):
    """
    Tool for generating text using Google Gemini 3 Pro model via GPTProto API.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invoke the Gemini text generation tool.
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

        temperature = tool_parameters.get("temperature", 0.7)
        max_tokens = tool_parameters.get("max_tokens", 4096)

        try:
            # Call API directly (no polling needed)
            result = self._generate_text(
                api_key=api_key,
                prompt=prompt,
                temperature=temperature,
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
        temperature: float,
        max_tokens: int,
    ) -> str | None:
        """
        Generate text using Gemini 3 Pro API.
        """
        url = f"{API_BASE}/models/gemini-3-pro-preview:generateContent"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "topP": 0.95,
                "topK": 64,
                "maxOutputTokens": max_tokens
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=60)

        if response.status_code != 200:
            raise Exception(f"API request failed: HTTP {response.status_code} - {response.text}")

        result = response.json()

        # Extract text from response
        # Response format: {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}
        candidates = result.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "")

        return None
