from google import genai
from google.genai import types
import os
import json
import logging

_client = None
def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client

async def plan_research(topic: str, depth: str) -> list[str]:
    """
    Planner Agent -> reads topic, outputs subtopics
    """
    try:
        client = _get_client()
        num_subtopics = {"Quick": 3, "Standard": 5, "Deep": 6}.get(depth, 5)
        
        prompt = f"""
        You are a Research Planner. Break the topic '{topic}' into {num_subtopics} focused, non-overlapping subtopics.
        Output ONLY a JSON array of strings. No markdown, no explanation.
        Example: ["Subtopic 1", "Subtopic 2"]
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
        
        subtopics = json.loads(text)
        if not isinstance(subtopics, list):
            raise ValueError("Output is not a list")
            
        return subtopics[:num_subtopics]
    except Exception as e:
        logging.error(f"Planner failed: {e}")
        return [f"{topic} overview", f"Key factors of {topic}", f"Future outlook on {topic}"]
