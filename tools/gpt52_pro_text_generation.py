from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

API_BASE = "https://gptproto.com/v1"


class Gpt52ProTextGenerationTool(Tool):
    """
    Tool for generating text, analyzing images, analyzing files, and searching the web
    using OpenAI GPT-5.2-Pro model via GPTProto API.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invoke the GPT-5.2-Pro text generation tool.
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
        enable_web_search = tool_parameters.get("enable_web_search", False)

        try:
            # Call API directly
            result = self._generate_text(
                api_key=api_key,
                prompt=prompt,
                image_url=image_url,
                file_url=file_url,
                enable_web_search=enable_web_search,
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
        image_url: str,
        file_url: str,
        enable_web_search: bool,
    ) -> str | None:
        """
        Generate text using GPT-5.2-Pro API.
        """
        url = f"{API_BASE}/responses"
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        # Build content array
        content = [
            {
                "type": "input_text",
                "text": prompt
            }
        ]

        # Add image if provided
        if image_url:
            content.append({
                "type": "input_image",
                "image_url": image_url
            })

        # Add file if provided
        if file_url:
            content.append({
                "type": "input_file",
                "file_url": file_url
            })

        # Build request data
        data = {
            "model": "gpt-5.2-pro",
            "input": [
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
                    "type": "web_search_preview"
                }
            ]

        response = requests.post(url, headers=headers, json=data, timeout=120)

        if response.status_code != 200:
            raise Exception(f"API request failed: HTTP {response.status_code} - {response.text}")

        result = response.json()

        # Extract text from response
        # Try common response formats
        if "output" in result:
            output = result["output"]
            if isinstance(output, str):
                return output
            elif isinstance(output, list) and len(output) > 0:
                # Handle array of output items
                for item in output:
                    if isinstance(item, dict):
                        if item.get("type") == "message":
                            content = item.get("content", [])
                            for c in content:
                                if isinstance(c, dict) and c.get("type") == "output_text":
                                    return c.get("text", "")
                        elif "text" in item:
                            return item["text"]
                    elif isinstance(item, str):
                        return item

        # Try other common fields
        if "text" in result:
            return result["text"]

        if "message" in result:
            message = result["message"]
            if isinstance(message, str):
                return message
            elif isinstance(message, dict):
                return message.get("content", "")

        if "choices" in result:
            choices = result["choices"]
            if choices and len(choices) > 0:
                choice = choices[0]
                if "message" in choice:
                    return choice["message"].get("content", "")
                elif "text" in choice:
                    return choice["text"]

        # Handle wrapped response
        if "data" in result:
            data_obj = result["data"]
            if isinstance(data_obj, dict):
                return data_obj.get("text") or data_obj.get("content") or data_obj.get("output")

        return None
