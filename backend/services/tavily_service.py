from tavily import TavilyClient
import os

api_key = os.getenv("TAVILY_API_KEY", "test_key")
try:
    tavily = TavilyClient(api_key=api_key)
except:
    tavily = None

async def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    if not tavily:
        return []
    try:
        response = tavily.search(query=query, search_depth="advanced", max_results=max_results)
        return [{"title": r["title"], "url": r["url"], "content": r["content"]} for r in response.get("results", [])]
    except Exception as e:
        print(f"Tavily search failed: {e}")
        return []
