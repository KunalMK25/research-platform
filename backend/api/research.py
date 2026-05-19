from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.db import get_db
from database.schemas import ResearchRequest, ResearchStatusResponse
from database.models import ResearchSession, SubTopic, Report
from agents.orchestrator import run_orchestrator, progress_store
import uuid
import asyncio
import json

router = APIRouter()

@router.post("/start")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    session_id = str(uuid.uuid4())
    new_session = ResearchSession(
        id=session_id,
        user_id=request.user_id,
        topic=request.topic,
        depth=request.depth,
        status="pending"
    )
    db.add(new_session)
    await db.commit()

    background_tasks.add_task(run_orchestrator, session_id, request.topic, request.depth)

    return {"session_id": session_id}


@router.get("/{session_id}/status")
async def get_status(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ResearchSession).filter(ResearchSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get subtopic count if available
    st_result = await db.execute(select(SubTopic).filter(SubTopic.session_id == session_id))
    subtopics = st_result.scalars().all()

    events = progress_store.get(session_id, [])
    latest = events[-1] if events else {"step": session.status, "message": f"Status: {session.status}", "detail": ""}

    return {
        "session_id": session_id,
        "status": session.status,
        "subtopics": [{"id": s.id, "title": s.title, "status": s.status} for s in subtopics],
        "progress": latest,
        "all_events": events,
    }


@router.get("/{session_id}/stream")
async def stream_progress(session_id: str):
    """Server-Sent Events endpoint for real-time progress."""
    async def event_generator():
        seen = 0
        for _ in range(300):  # max 5 min at 1s intervals
            events = progress_store.get(session_id, [])
            new_events = events[seen:]
            for ev in new_events:
                yield f"data: {json.dumps(ev)}\n\n"
            seen = len(events)

            # Check if done
            if any(e["step"] in ("completed", "failed") for e in events):
                yield f"data: {json.dumps({'step': 'done', 'message': 'Stream closed'})}\n\n"
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })


@router.get("/{session_id}/report")
async def get_report(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).filter(Report.session_id == session_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"markdown": report.markdown_content, "metrics": report.metrics_json}
