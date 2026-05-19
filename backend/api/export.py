from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.db import get_db
from database.models import Report

router = APIRouter()

@router.post("/pdf/{session_id}")
async def export_pdf(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).filter(Report.session_id == session_id))
    report = result.scalar_one_or_none()
    if not report or not report.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(report.pdf_path, media_type='application/pdf', filename=f"report_{session_id}.pdf")

@router.post("/ppt/{session_id}")
async def export_ppt(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report).filter(Report.session_id == session_id))
    report = result.scalar_one_or_none()
    if not report or not report.ppt_path:
        raise HTTPException(status_code=404, detail="PPT not found")
    
    return FileResponse(report.ppt_path, media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation', filename=f"presentation_{session_id}.pptx")
