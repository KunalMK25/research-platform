from google import genai
import os
import logging

_client = None
def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client

async def generate_report(topic: str, findings: list[dict], contradictions: list[str]) -> str:
    try:
        client = _get_client()
        
        findings_text = ""
        for i, f in enumerate(findings):
            findings_text += f"## Subtopic {i+1}\n{f.get('content', '')}\n\n"
            
        contradictions_text = "\n".join([f"- {c}" for c in contradictions]) if contradictions else "None identified."
        
        prompt = f"""
        Generate a professional markdown research report on the topic '{topic}'.
        
        Include these sections:
        # Executive Summary
        
        # Findings
        {findings_text}
        
        # Contradictions
        {contradictions_text}
        
        # References
        (List all unique URLs found in the findings)
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        logging.error(f"Reporter failed: {e}")
        return f"# Error generating report for {topic}\n\nPlease try again."
