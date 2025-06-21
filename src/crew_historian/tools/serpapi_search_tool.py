import os
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from serpapi import GoogleSearch
import logging

logger = logging.getLogger(__name__)

class SerpApiSearchInput(BaseModel):
    query: str = Field(..., description="Search query to find relevant historical visual materials")

class SerpApiSearchTool(BaseTool):
    name: str = "SerpAPI Search Tool"
    description: str = "Search using SerpAPI for historical visual materials and documents"
    args_schema: Type[BaseModel] = SerpApiSearchInput

    def _run(self, query: str) -> str:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            logger.warning("SERPAPI_API_KEY not found in environment variables")
            return f"SerpAPI API key not configured. Cannot search for '{query}'."

        try:
            # Step 1: Text search
            text_search = GoogleSearch({
                "api_key": api_key,
                "engine": "google",
                "q": query,
                "location": "Austin, Texas, United States",
                "google_domain": "google.com",
                "gl": "us",
                "hl": "en",
                "num": 3
            }).get_dict()

            organic_results = text_search.get("organic_results", [])
            result_summary = []
            for item in organic_results:
                result_summary.append(f"{item.get('title')} | {item.get('link')}")

            # Step 2: Image search
            image_search = GoogleSearch({
                "api_key": api_key,
                "engine": "google_images",
                "q": query,
                "num": 3
            }).get_dict()

            image_urls = [img.get("original") for img in image_search.get("images_results", []) if "original" in img]

            result = "\n".join(result_summary)
            if image_urls:
                result += "\n\nImage URLs:\n" + "\n".join(image_urls)

            return result

        except Exception as e:
            logger.error(f"SerpAPI error: {e}")
            return f"Search failed: {str(e)}"


# Optional: test tool
if __name__ == "__main__":
    os.environ["SERPAPI_API_KEY"] = "your_key_here"  # or keep it in a .env
    tool = SerpApiSearchTool()
    print(tool._run("History of photography in Japan"))
