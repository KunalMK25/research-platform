import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.db import AsyncSessionLocal
from database.models import ResearchSession, SubTopic, Source, Finding, Report
from agents.planner import plan_research
from agents.researcher import research_subtopic
from agents.verifier import verify_sources
from agents.synthesizer import synthesize_findings
from agents.reporter import generate_report
from evaluation.metrics import calculate_metrics
import uuid
import json
from typing import Dict, List
from collections import defaultdict
import asyncio

# In-memory progress store: session_id -> list of progress events
progress_store: Dict[str, List[dict]] = defaultdict(list)

def push_progress(session_id: str, step: str, message: str, detail: str = ""):
    """Push a progress event to the in-memory store."""
    progress_store[session_id].append({
        "step": step,
        "message": message,
        "detail": detail,
    })

async def process_subtopic(session_id: str, db_st, depth: str):
    """Research + verify + synthesize a single subtopic. Runs concurrently."""
    push_progress(session_id, "researching", f"🔍 Researching: {db_st.title}")

    raw_sources = await research_subtopic(db_st.title, depth)
    push_progress(session_id, "verifying", f"✅ Verifying sources for: {db_st.title}", f"{len(raw_sources)} sources found")

    verified, contradictions = await verify_sources(raw_sources)
    push_progress(session_id, "synthesizing", f"🧠 Synthesizing: {db_st.title}", f"{len(verified)} sources verified")

    syn_res = await synthesize_findings(db_st.title, verified, depth)
    push_progress(session_id, "synthesizing", f"✨ Done: {db_st.title}", syn_res.get("confidence", "Low") + " confidence")

    return verified, contradictions, syn_res


async def run_orchestrator(session_id: str, topic: str, depth: str):
    progress_store[session_id] = []  # reset

    async with AsyncSessionLocal() as db:
        session = await db.get(ResearchSession, session_id)
        if not session:
            return

        try:
            # ── 1. Plan ──────────────────────────────────────────────────
            session.status = "planning"
            await db.commit()
            push_progress(session_id, "planning", f"📋 Planning research on: {topic}")

            subtopics_list = await plan_research(topic, depth)
            push_progress(session_id, "planning", f"📌 Identified {len(subtopics_list)} subtopics", ", ".join(subtopics_list))

            db_subtopics = []
            for st in subtopics_list:
                db_st = SubTopic(id=str(uuid.uuid4()), session_id=session_id, title=st, status="pending")
                db.add(db_st)
                db_subtopics.append(db_st)
            await db.commit()

            # ── 2. Research, Verify & Synthesize — ALL IN PARALLEL ───────
            session.status = "researching"
            await db.commit()
            push_progress(session_id, "researching", f"🚀 Starting parallel research on {len(db_subtopics)} subtopics...")

            results = await asyncio.gather(
                *[process_subtopic(session_id, db_st, depth) for db_st in db_subtopics],
                return_exceptions=True
            )

            all_verified_sources = []
            all_contradictions = []
            db_findings = []

            for db_st, result in zip(db_subtopics, results):
                if isinstance(result, Exception):
                    push_progress(session_id, "error", f"⚠️ Failed on: {db_st.title}", str(result))
                    continue

                verified, contradictions, syn_res = result
                all_contradictions.extend(contradictions)
                all_verified_sources.extend(verified)

                for s in verified:
                    db_s = Source(
                        id=str(uuid.uuid4()),
                        session_id=session_id,
                        subtopic_id=db_st.id,
                        title=s.get("title", ""),
                        url=s.get("url", ""),
                        domain=s.get("domain", ""),
                        credibility_score=s.get("credibility_score", 0),
                        publish_date=None
                    )
                    db.add(db_s)

                db_f = Finding(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    subtopic_id=db_st.id,
                    content=syn_res.get("content", ""),
                    confidence=syn_res.get("confidence", "Low"),
                    citations=syn_res.get("citations", [])
                )
                db.add(db_f)
                db_findings.append(db_f)
                db_st.status = "completed"

            await db.commit()

            # ── 3. Report ────────────────────────────────────────────────
            session.status = "reporting"
            await db.commit()
            push_progress(session_id, "reporting", "📝 Generating final report...")

            report_md = await generate_report(
                topic,
                [{"content": f.content} for f in db_findings],
                all_contradictions
            )

            metrics = calculate_metrics(
                [{"citations": f.citations} for f in db_findings],
                all_verified_sources
            )

            db_report = Report(
                id=str(uuid.uuid4()),
                session_id=session_id,
                markdown_content=report_md,
                metrics_json=metrics
            )
            db.add(db_report)
            session.status = "completed"
            await db.commit()

            push_progress(session_id, "completed", f"🎉 Research complete! {len(db_findings)} findings, {len(all_verified_sources)} sources.")

        except Exception as e:
            session.status = "failed"
            await db.commit()
            push_progress(session_id, "failed", f"❌ Research failed: {e}")
            print(f"Orchestrator failed: {e}")
