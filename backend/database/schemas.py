from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ResearchRequest(BaseModel):
    topic: str
    depth: str = "Standard" # Quick, Standard, Deep
    user_id: str = "anonymous"

class SubTopicSchema(BaseModel):
    id: str
    title: str
    status: str

class ResearchStatusResponse(BaseModel):
    session_id: str
    status: str
    progress: Dict[str, Any]

class HistoryResponse(BaseModel):
    id: str
    topic: str
    depth: str
    status: str
    created_at: datetime
