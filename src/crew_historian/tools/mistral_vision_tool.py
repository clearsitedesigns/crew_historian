import os
import base64
import requests
from typing import Type
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from mistralai import Mistral


class MistralVisionInput(BaseModel):
    """Input schema for MistralVisionTool."""
    image_path_or_url: str = Field(..., description="Local image path or URL to analyze")


class MistralVisionTool(BaseTool):
    name: str = "Mistral Vision Tool"
    description: str = "Analyzes an image (via URL or local file) and provides a textual summary."
    args_schema: Type[BaseModel] = MistralVisionInput

    def _run(self, image_path_or_url: str) -> str:
        api_key = os.getenv("MISTRAL_API_KEY")
        model = "pixtral-12b-latest"

        if not api_key:
            return "[Error] MISTRAL_API_KEY not found in environment."

        client = Mistral(api_key=api_key)

        # Helper: Check if it's a valid image link
        def is_direct_image_url(url: str) -> bool:
            return any(url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp"])

        # Helper: Try extracting one image from a webpage
        def extract_image_from_html(url: str) -> str | None:
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")
                img_tags = soup.find_all("img")
                for img in img_tags:
                    src = img.get("src")
                    if src:
                        return src if src.startswith("http") else requests.compat.urljoin(url, src)
            except Exception as e:
                return None
            return None

        try:
            # Remote image handling
            if image_path_or_url.startswith("http"):
                if not is_direct_image_url(image_path_or_url):
                    new_url = extract_image_from_html(image_path_or_url)
                    if not new_url or not is_direct_image_url(new_url):
                        return "[MistralVisionTool Error] Unable to locate a valid image URL in the provided page."
                    image_path_or_url = new_url

                image_content = {
                    "type": "image_url",
                    "image_url": image_path_or_url
                }

            # Local file
            else:
                with open(image_path_or_url, "rb") as img_file:
                    encoded = base64.b64encode(img_file.read()).decode("utf-8")
                image_content = {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{encoded}"
                }

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image and summarize key visual insights."},
                        image_content
                    ]
                }
            ]

            response = client.chat.complete(model=model, messages=messages)
            return response.choices[0].message.content

        except Exception as e:
            return f"[MistralVisionTool Error] {str(e)}"
