from services.tavily_service import search_tavily
from services.arxiv_service import search_arxiv
import asyncio
from urllib.parse import urlparse

async def run_researcher(subtopics: list[str], depth: str = "Standard") -> dict[str, list[dict]]:
    """
    Researcher Agent -> searches each subtopic using Tavily + arXiv (if depth is Deep).
    Each source is structured as: {title, url, snippet, domain, source_type}.
    Returns a dict mapping subtopic -> list of sources.
    """
    results = {}
    for subtopic in subtopics:
        # 1. Tavily web search
        tavily_task = search_tavily(subtopic, max_results=5)
        
        # 2. arXiv academic search (only if depth is Deep)
        arxiv_task = None
        if depth == "Deep":
            arxiv_task = search_arxiv(subtopic, max_results=2)
            
        if arxiv_task:
            tavily_res, arxiv_res = await asyncio.gather(tavily_task, arxiv_task)
        else:
            tavily_res = await tavily_task
            arxiv_res = []
            
        combined = []
        # Process Tavily results
        for item in tavily_res:
            domain = urlparse(item["url"]).netloc
            combined.append({
                "title": item["title"],
                "url": item["url"],
                "snippet": item["content"],
                "domain": domain,
                "source_type": "web"
            })
            
        # Process arXiv results
        for item in arxiv_res:
            domain = urlparse(item["url"]).netloc
            combined.append({
                "title": item["title"],
                "url": item["url"],
                "snippet": item["content"],
                "domain": domain,
                "source_type": "academic"
            })
            
        results[subtopic] = combined
        
    return results

# Keep research_subtopic as a backwards-compatible wrapper
async def research_subtopic(subtopic: str, depth: str) -> list[dict]:
    res_dict = await run_researcher([subtopic], depth)
    return res_dict.get(subtopic, [])
