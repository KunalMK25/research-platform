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

async def run_synthesizer(verified_sources: dict, topic: str) -> dict[str, str]:
    """
    Synthesizer Agent -> writes a 150-200 word summary per subtopic under the topic.
    Every claim must reference a source with [Source: domain.com] inline.
    Returns a dict mapping subtopic -> synthesis paragraph (string).
    """
    client = _get_client()
    synthesis_results = {}
    
    for subtopic, sources in verified_sources.items():
        if not sources:
            synthesis_results[subtopic] = f"No verified sources were found to synthesize findings for the subtopic '{subtopic}'."
            continue
            
        try:
            sources_context = json.dumps([{"domain": s["domain"], "snippet": s["snippet"]} for s in sources])
            
            prompt = f"""
            You are a rigorous Synthesizer Agent.
            Write a cohesive, informative 150-200 word summary paragraph for the subtopic '{subtopic}' under the main research topic '{topic}'.
            
            Strict Guidelines:
            1. Every key claim, data point, or fact MUST be followed by an inline citation referencing the source domain in the EXACT format: [Source: domain.com].
            2. Integrate all findings smoothly into a cohesive narrative paragraph. Do not use bullet points or numbered lists.
            3. Do not include markdown headers, salutations, or concluding phrases. Output ONLY the plain text paragraph.
            4. Keep the summary between 150 and 200 words.
            
            Sources to use:
            {sources_context}
            """
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            synthesis_results[subtopic] = response.text.strip()
            
        except Exception as e:
            logging.error(f"Synthesizer failed for {subtopic}: {e}")
            synthesis_results[subtopic] = f"Failed to synthesize findings for '{subtopic}'."
            
    return synthesis_results

# Keep synthesize_findings as a backwards-compatible wrapper
async def synthesize_findings(subtopic: str, sources: list[dict], depth: str) -> dict:
    res = await run_synthesizer({subtopic: sources}, topic=subtopic)
    content = res.get(subtopic, "")
    citations = [s["url"] for s in sources if s.get("url")]
    return {
        "content": content,
        "confidence": "High" if len(sources) >= 3 else "Medium",
        "citations": citations
    }
