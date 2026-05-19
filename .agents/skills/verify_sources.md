# Skill: Verify Sources

## Objective
Score each gathered source for credibility and identify any contradictions between sources.

## Rules
- You are acting as **@verifier**.
- Be paranoid about misinformation.
- **Strict Constraint**: Assign a score from 1-10 to each source based on domain authority, freshness, and citation signals.
- **Strict Constraint**: Discard any sources scoring below 5. Do not include them in the final verified list.
- **Strict Constraint**: Explicitly flag any conflicting claims or contradictions found between the remaining sources.

## Output
Save the verified list of sources and any flagged contradictions to `production_artifacts/verified_sources.md`.