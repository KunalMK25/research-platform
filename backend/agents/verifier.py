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

async def verify_sources(sources: list[dict]) -> tuple[list[dict], list[str]]:
    if not sources:
        return [], []
        
    try:
        client = _get_client()
        sources_json = json.dumps([{"url": s["url"], "snippet": s["snippet"]} for s in sources])
        
        prompt = f"""
        Score each source from 1 to 10 based on domain trust and relevance.
        Also flag any major contradictions between the snippets.
        Input sources: {sources_json}
        
        Output JSON ONLY with this schema:
        {{
            "scores": {{"url1": score1, "url2": score2}},
            "contradictions": ["Contradiction 1..."]
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
        
        verified = []
        for s in sources:
            score = scores.get(s["url"], 5)
            if score >= 5:
                s["credibility_score"] = score
                verified.append(s)
                
        return verified, contradictions
    except Exception as e:
        logging.error(f"Verifier failed: {e}")
        for s in sources:
            s["credibility_score"] = 5
        return sources, []
