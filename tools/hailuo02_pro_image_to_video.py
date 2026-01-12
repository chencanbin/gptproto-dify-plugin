import time
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

API_BASE = "https://gptproto.com/api/v3"


class Hailuo02ProImageToVideoTool(Tool):
    """
    Tool for generating videos from images using MiniMax Hailuo 02 Pro model via GPTProto API.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invoke the Hailuo 02 Pro image-to-video tool.
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

        image = tool_parameters.get("image", "")
        if not image:
            yield self.create_text_message("Error: Start image URL is required")
            return

        end_image = tool_parameters.get("end_image", "")
        duration = int(tool_parameters.get("duration", "6"))
        resolution = tool_parameters.get("resolution", "768P")
        enable_prompt_expansion = tool_parameters.get("enable_prompt_expansion", True)
        go_fast = tool_parameters.get("go_fast", True)

        try:
            # Submit task
            result_id = self._submit_task(
                api_key=api_key,
                prompt=prompt,
                image=image,
                end_image=end_image,
                duration=duration,
                resolution=resolution,
                enable_prompt_expansion=enable_prompt_expansion,
                go_fast=go_fast,
            )

            if not result_id:
                yield self.create_text_message("Error: Failed to submit video generation task")
                return

            yield self.create_text_message(f"Task submitted, generating video... (ID: {result_id})")

            # Poll for result (longer timeout for video)
            video_url = self._poll_result(api_key=api_key, result_id=result_id)

            if video_url:
                yield self.create_json_message({"files": [{"url": video_url, "type": "video/mp4"}]})
                yield self.create_text_message(f"Video generated successfully!\n{video_url}")
            else:
                yield self.create_text_message("Error: Failed to get video result after timeout")

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

    def _submit_task(
        self,
        api_key: str,
        prompt: str,
        image: str,
        end_image: str,
        duration: int,
        resolution: str,
        enable_prompt_expansion: bool,
        go_fast: bool,
    ) -> str | None:
        """
        Submit image-to-video task.
        """
        url = f"{API_BASE}/minimax/hailuo-02/pro"
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        data = {
            "prompt": prompt,
            "image": image,
            "duration": duration,
            "resolution": resolution,
            "enable_prompt_expansion": enable_prompt_expansion,
            "go_fast": go_fast,
        }

        # Add end image if provided
        if end_image:
            data["end_image"] = end_image

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
            "Authorization": api_key,
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
