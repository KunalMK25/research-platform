import asyncio
import logging
import uuid
import time
from datetime import datetime, timezone
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import AsyncSessionLocal
from database.models import ResearchSession, SubTopic, Source, Finding, Report
from agents.planner import run_planner
from agents.researcher import run_researcher
from agents.verifier import run_verifier
from agents.synthesizer import run_synthesizer
from agents.reporter import run_reporter

# Configure logger
logger = logging.getLogger(__name__)

# Progress store: session_id -> list of progress event dicts
progress_store: dict[str, list] = defaultdict(list)

def push_progress(session_id: str, step: str, agent: str, message: str, detail: str = ""):
    """Push a structured progress event to the in-memory store."""
    event = {
        "step": step,
        "agent": agent,
        "message": message,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    progress_store[session_id].append(event)
    logger.info(f"[{step.upper()}] [{agent}] {message} - {detail}")

async def run_orchestrator(session_id: str, topic: str, depth: str):
    """
    Main async function that orchestrates the 5 sequential research agents:
    1. Planner -> breaks topic into subtopics
    2. Researcher -> gathers Tavily and arXiv sources
    3. Verifier -> scores and screens sources, aggregates contradictions
    4. Synthesizer -> summarizes findings with inline citations
    5. Reporter -> compiles final markdown report
    """
    start_time = time.time()
    progress_store[session_id] = []  # Reset progress events for this session

    async with AsyncSessionLocal() as db:
        session = await db.get(ResearchSession, session_id)
        if not session:
            logger.error(f"ResearchSession {session_id} not found in database.")
            return

        try:
            # ─────────────────────────────────────────────────────────────
            # 1. PLANNER AGENT
            # ─────────────────────────────────────────────────────────────
            session.status = "planning"
            await db.commit()
            
            push_progress(
                session_id=session_id,
                step="planning",
                agent="Planner",
                message=f"Starting planning phase for: '{topic}'",
                detail=f"Depth level: '{depth}'"
            )

            # Run planner to get list of subtopic strings
            subtopics_list = await run_planner(topic, depth)
            
            # Save SubTopic rows in the database
            db_subtopics = []
            for i, st_title in enumerate(subtopics_list):
                db_st = SubTopic(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    title=st_title,
                    status="pending",
                    order_index=i
                )
                db.add(db_st)
                db_subtopics.append(db_st)
            await db.commit()

            push_progress(
                session_id=session_id,
                step="planning",
                agent="Planner",
                message="Planning phase completed successfully.",
                detail=f"Identified subtopics: {', '.join(subtopics_list)}"
            )

            # ─────────────────────────────────────────────────────────────
            # 2. RESEARCHER AGENT
            # ─────────────────────────────────────────────────────────────
            session.status = "researching"
            await db.commit()

            push_progress(
                session_id=session_id,
                step="researching",
                agent="Researcher",
                message="Starting research collection phase...",
                detail=f"Gathering web & academic data for {len(subtopics_list)} subtopics"
            )

            # Update subtopic DB statuses to "searching"
            for db_st in db_subtopics:
                db_st.status = "searching"
            await db.commit()

            # Execute run_researcher
            sources_by_subtopic = await run_researcher(subtopics_list, depth)

            # Calculate total sources fetched
            total_sources = sum(len(sources) for sources in sources_by_subtopic.values())

            push_progress(
                session_id=session_id,
                step="researching",
                agent="Researcher",
                message="Research collection phase completed.",
                detail=f"Acquired {total_sources} total raw source listings"
            )

            # ─────────────────────────────────────────────────────────────
            # 3. VERIFIER AGENT
            # ─────────────────────────────────────────────────────────────
            session.status = "verifying"
            await db.commit()

            push_progress(
                session_id=session_id,
                step="verifying",
                agent="Verifier",
                message="Starting source evaluation and contradiction flagging...",
                detail="Scoring relevance and filtering out low-quality listings"
            )

            # Update subtopics to "verifying"
            for db_st in db_subtopics:
                db_st.status = "verifying"
            await db.commit()

            # Map the sources by the DB subtopic ID for correct foreign key mapping
            sources_by_subtopic_id = {}
            for db_st in db_subtopics:
                sources_by_subtopic_id[db_st.id] = sources_by_subtopic.get(db_st.title, [])

            # Run verifier (takes dict, returns dict with filtered sources and list of contradictions)
            # We pass a title-keyed dict to match run_verifier's logic
            verifier_input = {db_st.title: sources_by_subtopic.get(db_st.title, []) for db_st in db_subtopics}
            verifier_result = await run_verifier(verifier_input)
            
            verified_sources_by_title = verifier_result.get("verified_sources", {})
            all_contradictions = verifier_result.get("contradictions", [])

            # Save verified Source rows to the DB
            all_verified_sources_list = []
            for db_st in db_subtopics:
                verified_for_st = verified_sources_by_title.get(db_st.title, [])
                for s in verified_for_st:
                    db_s = Source(
                        id=str(uuid.uuid4()),
                        session_id=session_id,
                        subtopic_id=db_st.id,
                        title=s.get("title", ""),
                        url=s.get("url", ""),
                        domain=s.get("domain", ""),
                        credibility_score=s.get("credibility_score", 5),
                        publish_date=None
                    )
                    db.add(db_s)
                    all_verified_sources_list.append(s)
            await db.commit()

            push_progress(
                session_id=session_id,
                step="verifying",
                agent="Verifier",
                message="Source evaluation phase completed.",
                detail=f"Kept {len(all_verified_sources_list)} credible sources. Contradictions identified: {len(all_contradictions)}"
            )

            # ─────────────────────────────────────────────────────────────
            # 4. SYNTHESIZER AGENT
            # ─────────────────────────────────────────────────────────────
            session.status = "synthesizing"
            await db.commit()

            push_progress(
                session_id=session_id,
                step="synthesizing",
                agent="Synthesizer",
                message="Starting synthesized paragraph production...",
                detail="Drafting targeted findings with integrated inline domain citations"
            )

            # Run synthesizer (takes dict mapping subtopic -> verified sources, topic)
            # Returns dict mapping subtopic -> synthesis paragraph string
            synthesis_result = await run_synthesizer(verified_sources_by_title, topic)

            # Save Finding rows & update Subtopic DB status to "done"
            db_findings = []
            for db_st in db_subtopics:
                paragraph = synthesis_result.get(db_st.title, "")
                
                # Extract URLs as citations for DB schema
                verified_for_st = verified_sources_by_title.get(db_st.title, [])
                citations = [s["url"] for s in verified_for_st if "url" in s]

                db_f = Finding(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    subtopic_id=db_st.id,
                    content=paragraph,
                    confidence="High" if len(verified_for_st) >= 3 else "Medium",
                    citations=citations
                )
                db.add(db_f)
                db_findings.append(db_f)
                
                # Update status of subtopic to done
                db_st.status = "done"
                
            await db.commit()

            push_progress(
                session_id=session_id,
                step="synthesizing",
                agent="Synthesizer",
                message="Synthesis production phase completed.",
                detail="Synthesizer generated summaries with inline citations for all subtopics"
            )

            # ─────────────────────────────────────────────────────────────
            # 5. REPORTER AGENT
            # ─────────────────────────────────────────────────────────────
            session.status = "reporting"
            await db.commit()

            push_progress(
                session_id=session_id,
                step="reporting",
                agent="Reporter",
                message="Assembling final structured markdown report...",
                detail="Synthesizing Executive Summary, Findings, bibliography, and contradictions"
            )

            # Execute run_reporter
            report_md = await run_reporter(synthesis_result, all_contradictions, topic)

            # Calculate report metrics and time taken
            word_count = len(report_md.split())
            source_count = len(all_verified_sources_list)
            time_taken = time.time() - start_time

            metrics = {
                "word_count": word_count,
                "source_count": source_count,
                "time_taken": round(time_taken, 2),
                "citation_coverage": round((sum(1 for f in db_findings if f.citations) / len(db_findings) * 100) if db_findings else 0, 2),
                "source_diversity": len(set(s.get("domain") for s in all_verified_sources_list if s.get("domain"))),
                "contradiction_rate": round((len(all_contradictions) / len(db_findings) * 100) if db_findings else 0, 2),
                "depth_score": len(all_verified_sources_list) * len(db_findings)
            }

            # Save Report row in database
            from agents.reporter import generate_pdf, generate_ppt
            pdf_path_gen = generate_pdf(report_md, session_id)
            ppt_path_gen = generate_ppt(synthesis_result, topic, session_id)

            db_report = Report(
                id=str(uuid.uuid4()),
                session_id=session_id,
                markdown_content=report_md,
                metrics_json=metrics,
                pdf_path=pdf_path_gen if pdf_path_gen else None,
                ppt_path=ppt_path_gen if ppt_path_gen else None,
                created_at=datetime.now(timezone.utc)
            )
            db.add(db_report)

            session.status = "completed"
            session.completed_at = datetime.now(timezone.utc)
            await db.commit()

            push_progress(
                session_id=session_id,
                step="completed",
                agent="Reporter",
                message="Research process completed! Final report saved.",
                detail=f"Report length: {word_count} words | Verified sources: {source_count} | Duration: {round(time_taken, 1)} seconds"
            )

        except Exception as e:
            logger.error(f"Orchestration failure on session {session_id}: {e}", exc_info=True)
            try:
                session.status = "failed"
                await db.commit()
            except Exception as db_err:
                logger.error(f"Could not set session status to failed: {db_err}")
            
            push_progress(
                session_id=session_id,
                step="failed",
                agent="Orchestrator",
                message=f"Research failed: {str(e)}",
                detail="An error occurred during agent pipeline execution"
            )
