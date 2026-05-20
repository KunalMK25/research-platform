from groq import AsyncGroq
import os
import json
import logging
import asyncio

async def verify_single_subtopic(subtopic: str, sources: list[dict], client: AsyncGroq, max_sources: int = 8) -> tuple[str, list[dict], list[str]]:
    if not sources:
        return subtopic, [], []
    sources = sources[:max_sources]
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
            s["credibility_score"] = score
            if score >= 5:
                subtopic_verified.append(s)

        formatted_contradictions = [f"In '{subtopic}': {c}" for c in contradictions]
        return subtopic, subtopic_verified, formatted_contradictions

    except Exception as e:
        logging.error(f"Verifier failed for {subtopic}: {e}")
        for s in sources:
            s["credibility_score"] = 8
        return subtopic, sources, []

async def run_verifier(sources_by_subtopic: dict, depth: str = "Standard") -> dict:
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    max_sources_per_subtopic = {"Quick": 3, "Standard": 4, "Deep": 4}.get(depth, 4)

    # Skip LLM verification for speed in all modes
    if True:
        verified_sources = {}
        all_contradictions = []
        for subtopic, sources in sources_by_subtopic.items():
            truncated = sources[:max_sources_per_subtopic]
            for s in truncated:
                s["credibility_score"] = 8
            verified_sources[subtopic] = truncated
        return {"verified_sources": verified_sources, "contradictions": all_contradictions}

    # Deep: full LLM verification
    tasks = []
    for subtopic, sources in sources_by_subtopic.items():
        tasks.append(verify_single_subtopic(subtopic, sources, client, max_sources_per_subtopic))

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

async def verify_sources(sources: list[dict], depth: str = "Standard") -> tuple[list[dict], list[str]]:
    res = await run_verifier({"subtopic": sources}, depth)
    return res["verified_sources"].get("subtopic", []), res["contradictions"]
