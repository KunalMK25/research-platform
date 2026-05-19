from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.db import get_db
from database.models import ResearchSession
from database.schemas import HistoryResponse
from typing import List

router = APIRouter()

@router.get("/{user_id}", response_model=List[HistoryResponse])
async def get_history(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ResearchSession).filter(ResearchSession.user_id == user_id).order_by(ResearchSession.created_at.desc()))
    sessions = result.scalars().all()
    return [
        HistoryResponse(
            id=s.id,
            topic=s.topic,
            depth=s.depth,
            status=s.status,
            created_at=s.created_at
        ) for s in sessions
    ]
