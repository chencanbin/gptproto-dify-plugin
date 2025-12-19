import base64
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

API_BASE = "https://gptproto.com/v1beta"


class Gemini25ProTextGenerationTool(Tool):
    """
    Tool for generating text, analyzing images, and analyzing files
    using Google Gemini 2.5 Pro model via GPTProto API.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invoke the Gemini 2.5 Pro text generation tool.
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

        image_url = tool_parameters.get("image_url", "")
        file_url = tool_parameters.get("file_url", "")
        temperature = tool_parameters.get("temperature", 0.7)
        max_tokens = tool_parameters.get("max_tokens", 4096)

        try:
            # Call API directly (no polling needed)
            result = self._generate_text(
                api_key=api_key,
                prompt=prompt,
                image_url=image_url,
                file_url=file_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            if result:
                yield self.create_text_message(result)
            else:
                yield self.create_text_message("Error: Failed to generate text")

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

    def _get_mime_type(self, url: str) -> str:
        """
        Determine MIME type from URL extension.
        """
        url_lower = url.lower()
        if url_lower.endswith(".png"):
            return "image/png"
        elif url_lower.endswith(".gif"):
            return "image/gif"
        elif url_lower.endswith(".webp"):
            return "image/webp"
        elif url_lower.endswith(".pdf"):
            return "application/pdf"
        elif url_lower.endswith(".doc"):
            return "application/msword"
        elif url_lower.endswith(".docx"):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif url_lower.endswith(".txt"):
            return "text/plain"
        else:
            return "image/jpeg"  # Default for images

    def _download_and_encode_image(self, url: str) -> str | None:
        """
        Download image from URL and encode to base64.
        """
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode("utf-8")
        except Exception:
            pass
        return None

    def _generate_text(
        self,
        api_key: str,
        prompt: str,
        image_url: str,
        file_url: str,
        temperature: float,
        max_tokens: int,
    ) -> str | None:
        """
        Generate text using Gemini 2.5 Pro API.
        """
        url = f"{API_BASE}/models/gemini-2.5-pro:generateContent"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Build parts array
        parts = [{"text": prompt}]

        # Add image if provided (using inlineData with base64)
        if image_url:
            image_data = self._download_and_encode_image(image_url)
            if image_data:
                mime_type = self._get_mime_type(image_url)
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_data
                    }
                })

        # Add file if provided (using file_data with URL)
        if file_url:
            mime_type = self._get_mime_type(file_url)
            parts.append({
                "file_data": {
                    "mime_type": mime_type,
                    "file_uri": file_url
                }
            })

        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts
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

        response = requests.post(url, headers=headers, json=data, timeout=120)

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
