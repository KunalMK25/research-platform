from groq import Groq
import os
import logging
import re

async def run_planner(topic: str, depth: str) -> list[str]:
    """
    Planner Agent -> breaks topic into subtopics (3 for Quick, 5 for Standard, 6 for Deep)
    Uses Gemini to output ONLY a numbered list of subtopics.
    Returns a clean list of subtopic strings.
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        num_subtopics = {"Quick": 3, "Standard": 5, "Deep": 6}.get(depth, 5)
        
        prompt = f"""
        You are an expert Research Planner.
        Break the topic '{topic}' into exactly {num_subtopics} focused, high-quality, non-overlapping subtopics.
        
        Output ONLY a numbered list of these subtopics, with one subtopic per line. Do not include markdown, bold text, introductory remarks, or any other explanations.
        
        Format example:
        1. Subtopic name one
        2. Subtopic name two
        3. Subtopic name three
        """
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content
        text = result.strip()
        
        # Parse the numbered list
        lines = text.split("\n")
        subtopics = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            # Match lines starting with a number followed by dot, bracket, dash or space
            match = re.match(r'^\d+[\.\)\-]?\s*(.*)$', line_str)
            if match:
                val = match.group(1).strip()
                if val:
                    # Clean up quotes or asterisks if any
                    val = val.replace("*", "").replace("\"", "").replace("'", "").strip()
                    subtopics.append(val)
            else:
                cleaned = line_str.lstrip("-*+ ").replace("*", "").replace("\"", "").replace("'", "").strip()
                if cleaned:
                    subtopics.append(cleaned)
                    
        # Filter and restrict count
        subtopics = [st for st in subtopics if st]
        if not subtopics:
            raise ValueError("No subtopics parsed from Gemini response.")
            
        return subtopics[:num_subtopics]
    except Exception as e:
        logging.error(f"Planner failed: {e}")
        # robust fallback list to fully satisfy Quick, Standard, and Deep requests
        fallbacks = [
            f"Core Definitions and Conceptual Overview of {topic}",
            f"Primary Methodologies and Operational Architectures of {topic}",
            f"Current Technology Barriers and Implementation Bottlenecks in {topic}",
            f"Key Innovations and Cutting-Edge Developments in {topic}",
            f"Strategic Integration and Real-World Impact of {topic}",
            f"Future Research Frontiers and Long-Term Trends of {topic}"
        ]
        num_subtopics = {"Quick": 3, "Standard": 5, "Deep": 6}.get(depth, 5)
        return fallbacks[:num_subtopics]

# Keep plan_research as a backwards-compatible alias
async def plan_research(topic: str, depth: str) -> list[str]:
    return await run_planner(topic, depth)
