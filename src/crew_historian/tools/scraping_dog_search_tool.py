import os
import requests
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import logging

logger = logging.getLogger(__name__)

class ScrapingDogSearchInput(BaseModel):
    query: str = Field(..., description="Search query to find relevant historical visual materials")

class ScrapingDogSearchTool(BaseTool):
    name: str = "ScrapingDog Search Tool"
    description: str = "Search for historical visual materials and documents related to a given topic"
    args_schema: Type[BaseModel] = ScrapingDogSearchInput

    def _run(self, query: str) -> str:
        try:
            # Get API key in the run method
            api_key = os.getenv("SCRAPINGDOG_API_KEY")
            if not api_key:
                logger.warning("SCRAPINGDOG_API_KEY not found in environment variables")
                return f"ScrapingDog API key not configured. Cannot search for '{query}'."
            
            # Use ScrapingDog Google API endpoint (the correct one)
            search_results = self._search_with_scrapingdog_google(query, api_key, max_results=5)
            
            if not search_results:
                return f"No search results found for '{query}'. The search API may be unavailable or the query may need refinement."
            
            # Format results concisely to avoid token limits
            formatted_results = self._format_results_concisely(search_results, query)
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Search API error for '{query}': {str(e)}"

    def _search_with_scrapingdog_google(self, query: str, api_key: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search using ScrapingDog Google API endpoint"""
        try:
            # Use the CORRECT ScrapingDog Google endpoint
            url = "https://api.scrapingdog.com/google"
            
            params = {
                "api_key": api_key,
                "query": query,
                "results": max_results,  # Limit results
                "country": "us",
                "page": 0,
                "advance_search": "true",
                "ai_overview": "false"
            }
            
            logger.info(f"Making ScrapingDog Google API call for: {query}")
            response = requests.get(url, params=params, timeout=15)
            
            logger.info(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    results = []
                    
                    # Handle ScrapingDog Google API response format
                    organic_results = None
                    if isinstance(data, dict):
                        # ScrapingDog Google API typically uses 'organic_results'
                        organic_results = (data.get('organic_results') or 
                                         data.get('results') or 
                                         data.get('organic'))
                    
                    if organic_results and isinstance(organic_results, list):
                        logger.info(f"Found {len(organic_results)} organic results")
                        
                        for i, item in enumerate(organic_results[:max_results]):
                            if isinstance(item, dict):
                                # Extract essential information only
                                title = item.get('title', item.get('name', f'Result {i+1}'))
                                url = item.get('link', item.get('url', ''))
                                snippet = item.get('snippet', item.get('description', ''))
                                
                                result = {
                                    'title': str(title)[:100] if title else f'Result {i+1}',  # Limit length
                                    'url': str(url) if url else '',
                                    'snippet': str(snippet)[:200] if snippet else '',  # Limit length
                                    'type': self._determine_content_type(str(title), str(snippet))
                                }
                                
                                # Only include results with actual URLs
                                if result['url'] and not result['url'].startswith('javascript:'):
                                    results.append(result)
                                    logger.info(f"Added result {i+1}: {result['title'][:50]}...")
                    else:
                        logger.warning(f"No organic_results found. Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        logger.info(f"Sample data: {str(data)[:300]}...")
                        
                    return results
                    
                except Exception as json_error:
                    logger.error(f"JSON parsing error: {json_error}")
                    logger.error(f"Raw response: {response.text[:500]}...")
                    return []
            else:
                logger.error(f"API request failed with status {response.status_code}")
                logger.error(f"Response text: {response.text[:500]}...")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("ScrapingDog API request timed out")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"ScrapingDog API request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in ScrapingDog search: {e}")
            return []

    def _determine_content_type(self, title: str, snippet: str) -> str:
        """Determine the type of content based on title and snippet"""
        text = (title + " " + snippet).lower()
        
        if any(word in text for word in ['photo', 'photograph', 'image', 'picture', 'getty', 'photography']):
            return 'photograph'
        elif any(word in text for word in ['art', 'painting', 'artwork', 'sculpture', 'artist', 'gallery', 'exhibition']):
            return 'artwork'
        elif any(word in text for word in ['museum', 'collection', 'archive', 'smithsonian', 'moma', 'met']):
            return 'museum'
        elif any(word in text for word in ['library', 'digital collection', 'repository', 'loc.gov']):
            return 'library'
        elif any(word in text for word in ['document', 'manuscript', 'letter', 'paper']):
            return 'document'
        elif any(word in text for word in ['map', 'atlas', 'cartography', 'geographical']):
            return 'map'
        else:
            return 'web'

    def _format_results_concisely(self, results: List[Dict[str, Any]], query: str) -> str:
        """Format search results in a very concise manner to prevent token overflow"""
        if not results:
            return f"No results returned from search API for '{query}'."
        
        # Create a very concise summary
        output = [f"Found {len(results)} search results for '{query}':\n"]
        
        for i, result in enumerate(results, 1):
            # Very concise format - just essential info
            title = result['title'][:50] + '...' if len(result['title']) > 50 else result['title']
            line = f"{i}. {title}"
            
            if result['url']:
                # Shorten long URLs
                url = result['url']
                if len(url) > 60:
                    url = url[:57] + '...'
                line += f" | {url}"
            
            line += f" | {result['type']}"
            
            # Add snippet only if it's very short
            if result['snippet'] and len(result['snippet']) <= 80:
                line += f" | {result['snippet']}"
            
            output.append(line)
        
        # Keep total output under control
        full_output = "\n".join(output)
        if len(full_output) > 1500:  # If too long, truncate
            truncated = "\n".join(output[:4])  # Take first 3 results + header
            truncated += f"\n\n(Showing first 3 results to manage context. Total: {len(results)} found)"
            return truncated
            
        return full_output

# Test function
def test_tool():
    """Test the search tool with a simple query"""
    tool = ScrapingDogSearchTool()
    result = tool._run("1960s pop art")
    print("Search Results:")
    print(result)
    print(f"\nResult length: {len(result)} characters")

if __name__ == "__main__":
    test_tool()