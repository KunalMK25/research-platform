import arxiv

async def search_arxiv(query: str, max_results: int = 2) -> list[dict]:
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for r in client.results(search):
            results.append({
                "title": r.title,
                "url": r.entry_id,
                "content": r.summary
            })
        return results
    except Exception as e:
        print(f"ArXiv search failed: {e}")
        return []
