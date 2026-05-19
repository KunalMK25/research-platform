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

async def synthesize_findings(subtopic: str, sources: list[dict], depth: str) -> dict:
    if not sources:
        return {"content": f"No verified sources found for {subtopic}.", "citations": [], "confidence": "Low"}
        
    try:
        client = _get_client()
        sources_context = json.dumps([{"url": s["url"], "snippet": s["snippet"]} for s in sources])
        
        prompt = f"""
        Synthesize the following sources for the subtopic: '{subtopic}'.
        Write a cohesive summary. Every single claim MUST be followed by a citation in the format [Source: URL].
        If no source supports a claim, mark it as [UNVERIFIED].
        Sources: {sources_context}
        
        Output JSON ONLY:
        {{
            "content": "The synthesized text here...",
            "confidence": "High" | "Medium" | "Low",
            "citations": ["url1", "url2"]
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
        return result
    except Exception as e:
        logging.error(f"Synthesizer failed: {e}")
        return {
            "content": f"Failed to synthesize for {subtopic}.",
            "confidence": "Low",
            "citations": []
        }
