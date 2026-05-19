from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class ResearchRequest(BaseModel):
    topic: str
    depth: str
    user_id: Optional[str] = None

class SubTopicSchema(BaseModel):
    id: str
    title: str
    status: str
    order_index: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class ResearchStatusResponse(BaseModel):
    session_id: str
    status: str
    subtopics: List[SubTopicSchema]
    progress: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)

class HistoryResponse(BaseModel):
    id: str
    topic: str
    depth: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
