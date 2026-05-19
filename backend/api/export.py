from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.db import get_db
from database.models import Report, ResearchSession, Finding, SubTopic
from agents.reporter import generate_pdf, generate_ppt
import os

router = APIRouter()

@router.post("/pdf/{session_id}")
async def export_pdf(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).filter(Report.session_id == session_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this session")
    
    # If PDF is not yet generated or the file is missing, generate it on the fly
    if not report.pdf_path or not os.path.exists(report.pdf_path):
        pdf_path = generate_pdf(report.markdown_content, session_id)
        if not pdf_path:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
        
        report.pdf_path = pdf_path
        await db.commit()
    
    return FileResponse(report.pdf_path, media_type='application/pdf', filename=f"report_{session_id}.pdf")

@router.post("/ppt/{session_id}")
async def export_ppt(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).filter(Report.session_id == session_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this session")
    
    # If PPT is not yet generated or the file is missing, generate it on the fly
    if not report.ppt_path or not os.path.exists(report.ppt_path):
        # 1. Fetch research session to get topic title
        session_res = await db.execute(select(ResearchSession).filter(ResearchSession.id == session_id))
        session = session_res.scalar_one_or_none()
        topic = session.topic if session else "Research Briefing"
        
        # 2. Fetch findings and reconstruct synthesis dictionary
        findings_res = await db.execute(select(Finding).filter(Finding.session_id == session_id))
        findings = findings_res.scalars().all()
        
        synthesis = {}
        for f in findings:
            st_res = await db.execute(select(SubTopic).filter(SubTopic.id == f.subtopic_id))
            st = st_res.scalar_one_or_none()
            st_title = st.title if st else f"Topic Summary {f.id[:8]}"
            synthesis[st_title] = f.content or "No summary content available."
            
        if not synthesis:
            synthesis = {"Executive Summary": report.markdown_content[:300] + "..."}
            
        ppt_path = generate_ppt(synthesis, topic, session_id)
        if not ppt_path:
            raise HTTPException(status_code=500, detail="Failed to generate PPT presentation")
            
        report.ppt_path = ppt_path
        await db.commit()
        
    return FileResponse(report.ppt_path, media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation', filename=f"presentation_{session_id}.pptx")
