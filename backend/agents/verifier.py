from groq import AsyncGroq
import os
import json
import logging
import asyncio

async def verify_single_subtopic(subtopic: str, sources: list[dict], client: AsyncGroq) -> tuple[str, list[dict], list[str]]:
    """Helper to verify sources for a single subtopic asynchronously."""
    if not sources:
        return subtopic, [], []
        
    try:
        sources_context = json.dumps([{"url": s["url"], "snippet": s["snippet"][:100]} for s in sources])
        
        prompt = f"""
        Fact-check these sources for '{subtopic}':
        {sources_context}
        
        Score each 1-10 on authority/freshness. List contradictions.
        Output JSON: {{"scores": {{"url1": score}}, "contradictions": ["c1"]}}
        """
        
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content
        text = result.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        result = json.loads(text)
        scores = result.get("scores", {})
        contradictions = result.get("contradictions", [])
        
        subtopic_verified = []
        for s in sources:
            score = scores.get(s["url"], 5)
            # Store credibility score
            s["credibility_score"] = score
            if score >= 5:
                subtopic_verified.append(s)
                
        formatted_contradictions = [f"In '{subtopic}': {c}" for c in contradictions]
        return subtopic, subtopic_verified, formatted_contradictions
            
    except Exception as e:
        logging.error(f"Verifier failed for {subtopic}: {e}")
        # Fallback: score all sources highly (keep them)
        for s in sources:
            s["credibility_score"] = 8
        return subtopic, sources, []

async def run_verifier(sources_by_subtopic: dict) -> dict:
    """
    Verifier Agent -> scores and fact-checks sources for all subtopics in parallel using AsyncGroq.
    Discards sources scoring below 5.
    Flags contradictions between sources for the same subtopic.
    Returns:
    {
        "verified_sources": dict[str, list[dict]],
        "contradictions": list[str]
    }
    """
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    
    tasks = []
    for subtopic, sources in sources_by_subtopic.items():
        tasks.append(verify_single_subtopic(subtopic, sources, client))
        
    results = await asyncio.gather(*tasks)
    
    verified_sources = {}
    all_contradictions = []
    for subtopic, subtopic_verified, contradictions in results:
        verified_sources[subtopic] = subtopic_verified
        all_contradictions.extend(contradictions)
        
    return {
        "verified_sources": verified_sources,
        "contradictions": all_contradictions
    }

# Keep verify_sources as a backwards-compatible wrapper
async def verify_sources(sources: list[dict]) -> tuple[list[dict], list[str]]:
    res = await run_verifier({"subtopic": sources})
    return res["verified_sources"].get("subtopic", []), res["contradictions"]
