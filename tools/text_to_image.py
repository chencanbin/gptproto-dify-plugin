from collections.abc import Generator
from typing import Any
import time
import requests

from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


BASE_URL = "https://gptproto.com/api/v3"
API_KEY = "sk-83a0c6d0768b4909b7c37851159a48fb"


class TextToImageTool(Tool):
    """
    Text to Image Tool
    使用 GPTProto Gemini-3-Pro API 生成图像
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        执行文生图工具
        """
        # 获取参数
        prompt = tool_parameters.get("prompt", "")
        size = tool_parameters.get("size", "1K")
        aspect_ratio = tool_parameters.get("aspect_ratio", "1:1")
        output_format = tool_parameters.get("output_format", "png")

        if not prompt:
            yield self.create_text_message("Error: Prompt is required")
            return

        # 使用硬编码的 API Key
        api_key = API_KEY

        try:
            # 1. 提交任务
            submit_response = requests.post(
                f"{BASE_URL}/google/gemini-3-pro-image-preview/text-to-image",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": prompt,
                    "size": size,
                    "aspect_ratio": aspect_ratio,
                    "output_format": output_format,
                },
                timeout=30,
            )

            if not submit_response.ok:
                yield self.create_text_message(
                    f"Error submitting task: {submit_response.status_code} - {submit_response.text}"
                )
                return

            submit_data = submit_response.json()
            result_id = (
                submit_data.get("result_id")
                or submit_data.get("id")
                or submit_data.get("prediction_id")
            )

            if not result_id:
                yield self.create_text_message("Error: No result ID returned")
                return

            # 2. 轮询等待结果
            max_attempts = 150  # 最多等待5分钟 (150 * 2秒)
            for attempt in range(max_attempts):
                result_response = requests.get(
                    f"{BASE_URL}/predictions/{result_id}/result",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=30,
                )

                if not result_response.ok:
                    yield self.create_text_message(
                        f"Error getting result: {result_response.status_code}"
                    )
                    return

                result_data = result_response.json()
                status = result_data.get("status", "")

                if status in ["succeeded", "completed"]:
                    # 获取图像 URL
                    image_url = (
                        result_data.get("output")
                        or result_data.get("url")
                        or result_data.get("image_url")
                    )

                    if image_url:
                        # 返回图像
                        yield self.create_image_message(image_url)
                        yield self.create_text_message(
                            f"Image generated successfully!\n"
                            f"- Prompt: {prompt}\n"
                            f"- Size: {size}\n"
                            f"- Aspect Ratio: {aspect_ratio}\n"
                            f"- Format: {output_format}"
                        )
                    else:
                        yield self.create_text_message(
                            "Error: No image URL in response"
                        )
                    return

                elif status in ["failed", "error"]:
                    error_msg = result_data.get("error", "Unknown error")
                    yield self.create_text_message(f"Image generation failed: {error_msg}")
                    return

                # 继续等待
                time.sleep(2)

            yield self.create_text_message("Error: Timeout waiting for image generation")

        except requests.RequestException as e:
            yield self.create_text_message(f"Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
