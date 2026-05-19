from services.tavily_service import search_tavily
from services.arxiv_service import search_arxiv
import asyncio
from urllib.parse import urlparse

async def research_subtopic(subtopic: str, depth: str) -> list[dict]:
    num_sources = {"Quick": 3, "Standard": 5, "Deep": 8}.get(depth, 5)
    
    tavily_task = search_tavily(subtopic, max_results=num_sources - 1)
    arxiv_task = search_arxiv(subtopic, max_results=1)
    
    tavily_res, arxiv_res = await asyncio.gather(tavily_task, arxiv_task)
    combined = tavily_res + arxiv_res
    
    formatted_sources = []
    for item in combined:
        domain = urlparse(item["url"]).netloc
        formatted_sources.append({
            "title": item["title"],
            "url": item["url"],
            "domain": domain,
            "snippet": item["content"],
            "credibility_score": None
        })
        
    return formatted_sources
