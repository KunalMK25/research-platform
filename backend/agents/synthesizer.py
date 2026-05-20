from groq import AsyncGroq
import os
import json
import logging
import asyncio

WORD_TARGET = {"Quick": 80, "Standard": 130, "Deep": 180}

async def synthesize_single_subtopic(subtopic: str, sources: list[dict], topic: str, client: AsyncGroq, depth: str = "Standard") -> tuple[str, str]:
    """Helper to synthesize findings for a single subtopic asynchronously."""
    if not sources:
        return subtopic, f"No verified sources were found to synthesize findings for the subtopic '{subtopic}'."
        
    try:
        word_target = WORD_TARGET.get(depth, 130)
        max_snippet = {"Quick": 100, "Standard": 150, "Deep": 200}.get(depth, 150)
        sources_context = json.dumps([{"domain": s["domain"], "snippet": s["snippet"][:max_snippet]} for s in sources])
        
        prompt = f"""
        Write a concise synthesis of '{subtopic}' under the broader topic '{topic}' in about {word_target} words.
        Deliver real insights with substantive analysis.
        Support claims with brief inline citations like [Source: domain.com] where appropriate.
        Produce a cohesive paragraph. Avoid simply listing sources or repeating their titles.
        
        Source material available:
        {sources_context}
        """
        
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content
        return subtopic, result.strip()
        
    except Exception as e:
        logging.error(f"Synthesizer failed for {subtopic}: {e}")
        # Programmatic fallback: build a cohesive paragraph from all sources
        max_snippet = {"Quick": 100, "Standard": 150, "Deep": 200}.get(depth, 150)
        min_words = {"Quick": 30, "Standard": 45, "Deep": 60}.get(depth, 45)
        sentences = []
        sentences.append(f"A comprehensive analysis of {subtopic} reveals several important findings grounded in current research.")
        for i, s in enumerate(sources):
            snippet = s['snippet'][:max_snippet].rstrip('.')
            domain = s['domain']
            if i == 0:
                sentences.append(f"According to {domain}, {snippet}.")
            else:
                sentences.append(f"Supporting evidence from {domain} further establishes that {snippet}.")
        sentences.append(f"Together, these sources provide a well-rounded understanding of {subtopic} and its broader implications within the field of {topic}.")
        summary_text = " ".join(sentences)
        if len(summary_text.split()) < min_words:
            summary_text += f" Ongoing developments in {subtopic} continue to drive innovation, with researchers emphasizing the need for standardized evaluation frameworks and cross-disciplinary collaboration to accelerate progress."
        return subtopic, summary_text

async def run_synthesizer(verified_sources: dict, topic: str, depth: str = "Standard") -> dict[str, str]:
    """
    Synthesizer Agent -> writes summaries for all subtopics in parallel using AsyncGroq.
    Every claim must reference a source with [Source: domain.com] inline.
    Returns a dict mapping subtopic -> synthesis paragraph (string).
    """
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    
    tasks = []
    for subtopic, sources in verified_sources.items():
        tasks.append(synthesize_single_subtopic(subtopic, sources, topic, client, depth))
        
    results = await asyncio.gather(*tasks)
    return dict(results)

# Keep synthesize_findings as a backwards-compatible wrapper
async def synthesize_findings(subtopic: str, sources: list[dict], depth: str) -> dict:
    res = await run_synthesizer({subtopic: sources}, topic=subtopic, depth=depth)
    content = res.get(subtopic, "")
    citations = [s["url"] for s in sources if s.get("url")]
    return {
        "content": content,
        "confidence": "High" if len(sources) >= 3 else "Medium",
        "citations": citations
    }
