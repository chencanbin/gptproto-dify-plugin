import time
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

API_BASE = "https://gptproto.com/api/v3"


class SoraImageToVideoTool(Tool):
    """
    Tool for generating videos from images using OpenAI Sora 2 model via GPTProto API.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invoke the Sora image-to-video tool.
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

        images = tool_parameters.get("images", "")
        if not images:
            yield self.create_text_message("Error: Image URL is required")
            return

        duration = tool_parameters.get("duration", 5)
        orientation = tool_parameters.get("orientation", "landscape")
        size = tool_parameters.get("size", "small")
        character_url = tool_parameters.get("character_url", "")

        try:
            # Submit task
            result_id = self._submit_task(
                api_key=api_key,
                prompt=prompt,
                images=images,
                duration=duration,
                orientation=orientation,
                size=size,
                character_url=character_url,
            )

            if not result_id:
                yield self.create_text_message("Error: Failed to submit video generation task")
                return

            yield self.create_text_message(f"Task submitted, generating video... (ID: {result_id})")

            # Poll for result (longer timeout for video)
            video_url = self._poll_result(api_key=api_key, result_id=result_id)

            if video_url:
                yield self.create_link_message(video_url)
                yield self.create_text_message(f"Video generated successfully!\n{video_url}")
            else:
                yield self.create_text_message("Error: Failed to get video result after timeout")

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

    def _submit_task(
        self,
        api_key: str,
        prompt: str,
        images: str,
        duration: int,
        orientation: str,
        size: str,
        character_url: str,
    ) -> str | None:
        """
        Submit image-to-video task.
        """
        url = f"{API_BASE}/openai/reverse/sora-2/image-to-video"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Parse images (could be comma-separated)
        image_list = [img.strip() for img in images.split(",") if img.strip()]

        data = {
            "model": "sora-2",
            "prompt": prompt,
            "images": image_list,
            "duration": duration,
            "orientation": orientation,
            "size": size,
        }

        if character_url:
            data["character_url"] = character_url

        response = requests.post(url, headers=headers, json=data, timeout=60)

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
        max_attempts: int = 180,  # 6 minutes for video
        poll_interval: int = 2,
    ) -> str | None:
        """
        Poll for task result.
        """
        url = f"{API_BASE}/predictions/{result_id}/result"
        headers = {
            "Authorization": f"Bearer {api_key}",
        }

        for _ in range(max_attempts):
            try:
                response = requests.get(url, headers=headers, timeout=30)

                if response.status_code == 200:
                    result = response.json()

                    # Handle wrapped response
                    data = result.get("data", result)

                    # Check if task is completed
                    status = data.get("status", "").lower()

                    if status in ("succeeded", "completed", "success"):
                        # Try to extract video URL
                        outputs = data.get("outputs")
                        if isinstance(outputs, list) and len(outputs) > 0:
                            return outputs[0]

                        output = data.get("output")
                        if isinstance(output, list) and len(output) > 0:
                            return output[0]
                        elif isinstance(output, str):
                            return output

                        return (
                            data.get("video_url")
                            or data.get("url")
                            or data.get("result")
                        )

                    elif status in ("failed", "error"):
                        error_msg = data.get("error") or result.get("message") or "Unknown error"
                        raise Exception(f"Task failed: {error_msg}")

            except requests.exceptions.RequestException:
                pass

            time.sleep(poll_interval)

        return None
