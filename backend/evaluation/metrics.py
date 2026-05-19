def calculate_metrics(findings: list, sources: list) -> dict:
    total_claims = len(findings)
    claims_with_citations = sum(1 for f in findings if f.get("citations"))
    
    unique_domains = set(s.get("domain") for s in sources if s.get("domain"))
    
    # Mockup for contradiction rate
    contradictions = sum(1 for s in sources if s.get("credibility_score", 10) < 5)
    
    return {
        "citation_coverage": (claims_with_citations / total_claims * 100) if total_claims > 0 else 0,
        "source_diversity": len(unique_domains),
        "contradiction_rate": (contradictions / total_claims * 100) if total_claims > 0 else 0,
        "depth_score": len(sources) * len(findings)
    }
