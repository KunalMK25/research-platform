from google import genai
import os
import json
import logging

_client = None
def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client

async def run_verifier(sources_by_subtopic: dict) -> dict:
    """
    Verifier Agent -> scores each source 1-10 based on domain authority, freshness.
    Discards sources scoring below 5.
    Flags contradictions between sources for the same subtopic.
    Returns:
    {
        "verified_sources": dict[str, list[dict]],
        "contradictions": list[str]
    }
    """
    client = _get_client()
    verified_sources = {}
    all_contradictions = []
    
    for subtopic, sources in sources_by_subtopic.items():
        if not sources:
            verified_sources[subtopic] = []
            continue
            
        try:
            sources_context = json.dumps([{"url": s["url"], "snippet": s["snippet"]} for s in sources])
            
            prompt = f"""
            You are a rigorous Fact-Verification Agent.
            Evaluate the credibility of the following sources for the subtopic '{subtopic}':
            {sources_context}
            
            1. Score each source from 1 to 10 based on domain authority, freshness, and reliability.
            2. Scan the source snippets and explicitly identify any contradictions, conflicting claims, or key discrepancies.
            
            Output JSON ONLY with this schema:
            {{
                "scores": {{"url1": score1, "url2": score2}},
                "contradictions": ["Contradiction statement 1...", "Contradiction statement 2..."]
            }}
            """
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            text = response.text.strip()
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
                    
            verified_sources[subtopic] = subtopic_verified
            # Add subtopic prefix to contradictions for clarity
            for c in contradictions:
                all_contradictions.append(f"In '{subtopic}': {c}")
                
        except Exception as e:
            logging.error(f"Verifier failed for {subtopic}: {e}")
            # Fallback: score all sources as 5 (keep them)
            for s in sources:
                s["credibility_score"] = 5
            verified_sources[subtopic] = sources
            
    return {
        "verified_sources": verified_sources,
        "contradictions": all_contradictions
    }

# Keep verify_sources as a backwards-compatible wrapper
async def verify_sources(sources: list[dict]) -> tuple[list[dict], list[str]]:
    res = await run_verifier({"subtopic": sources})
    return res["verified_sources"].get("subtopic", []), res["contradictions"]
