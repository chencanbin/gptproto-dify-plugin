import time
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

API_BASE = "https://gptproto.com/api/v3"


class GptImageTextToImageTool(Tool):
    """
    Tool for generating images from text using OpenAI GPT-Image-1 model via GPTProto API.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invoke the GPT-Image-1 text-to-image tool.
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

        quality = tool_parameters.get("quality", "medium")
        size = tool_parameters.get("size", "1024x1024")
        background = tool_parameters.get("background", "auto")

        try:
            # Submit task
            result_id = self._submit_task(
                api_key=api_key,
                prompt=prompt,
                quality=quality,
                size=size,
                background=background,
            )

            if not result_id:
                yield self.create_text_message("Error: Failed to submit image generation task")
                return

            yield self.create_text_message(f"Task submitted, waiting for result... (ID: {result_id})")

            # Poll for result
            image_url = self._poll_result(api_key=api_key, result_id=result_id)

            if image_url:
                yield self.create_image_message(image_url)
                yield self.create_text_message(f"Image generated successfully!\n{image_url}")
            else:
                yield self.create_text_message("Error: Failed to get image result after timeout")

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

    def _submit_task(
        self,
        api_key: str,
        prompt: str,
        quality: str,
        size: str,
        background: str,
    ) -> str | None:
        """
        Submit image generation task.
        """
        url = f"{API_BASE}/openai/gpt-image-1/text-to-image"
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }
        data = {
            "prompt": prompt,
            "quality": quality,
            "size": size,
            "background": background,
            "enable_sync_mode": False,
            "response_format": "url",
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code != 200:
            raise Exception(f"Failed to submit task: HTTP {response.status_code} - {response.text}")

        result = response.json()

        # Handle wrapped response: {"data": {...}, "code": 200}
        data_obj = result.get("data", result)

        # Extract result_id from response
        if isinstance(data_obj, dict):
            return data_obj.get("id") or data_obj.get("result_id") or data_obj.get("task_id")

        return None

    def _poll_result(
        self,
        api_key: str,
        result_id: str,
        max_attempts: int = 60,
        poll_interval: int = 2,
    ) -> str | None:
        """
        Poll for task result.
        """
        url = f"{API_BASE}/predictions/{result_id}/result"
        headers = {
            "Authorization": api_key,
        }

        for _ in range(max_attempts):
            try:
                response = requests.get(url, headers=headers, timeout=30)

                if response.status_code == 200:
                    result = response.json()

                    # Handle wrapped response: {"data": {...}, "code": 200}
                    data = result.get("data", result)

                    # Check if task is completed
                    status = data.get("status", "").lower()

                    if status in ("succeeded", "completed", "success"):
                        # Try to extract image URL from "outputs" array first
                        outputs = data.get("outputs")
                        if isinstance(outputs, list) and len(outputs) > 0:
                            return outputs[0]

                        # Fallback to "output" field
                        output = data.get("output")
                        if isinstance(output, list) and len(output) > 0:
                            return output[0]
                        elif isinstance(output, str):
                            return output

                        # Try other common fields
                        return (
                            data.get("image_url")
                            or data.get("url")
                            or data.get("result")
                        )

                    elif status in ("failed", "error"):
                        error_msg = data.get("error") or result.get("message") or "Unknown error"
                        raise Exception(f"Task failed: {error_msg}")

                    # Still processing, continue polling

            except requests.exceptions.RequestException:
                # Network error, continue trying
                pass

            time.sleep(poll_interval)

        return None
