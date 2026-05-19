---
description: Run the full autonomous research pipeline on a given topic
---

# Workflow: Research

When the user types `/research <topic>`, execute the following pipeline using the roles defined in `.agents/agents.md` and the skill files in `.agents/skills/`:

## Execution Sequence

1. **Planning Step**: Act as **@planner** and execute `.agents/skills/plan_research.md` with the `<topic>`.
   > **HUMAN APPROVAL GATE**: Pause and ask the user for approval. Do not proceed until the user explicitly approves the research plan (e.g., by saying "Approved"). If the user requests changes or edits `production_artifacts/research_plan.md`, loop this step.

2. **Research Step**: Act as **@researcher** and execute `.agents/skills/gather_sources.md` for all the approved subtopics.

3. **Verification Step**: Act as **@verifier** and execute `.agents/skills/verify_sources.md` to score and filter the sources.

4. **Synthesis Step**: Act as **@synthesizer** and execute `.agents/skills/synthesize_findings.md` to summarize verified findings with citations.

5. **Reporting Step**: Act as **@reporter** and execute `.agents/skills/generate_report.md` to compile the final structured research report.

6. **Completion**: Present the path to the final report (`app_build/report.md`) to the user.