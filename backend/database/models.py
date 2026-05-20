from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.db import Base

class ResearchSession(Base):
    __tablename__ = "research_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    topic = Column(String, nullable=False)
    depth = Column(String, nullable=False) # Quick/Standard/Deep
    status = Column(String, nullable=False) # pending/running/completed/failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    subtopics = relationship("SubTopic", back_populates="session", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="session", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="session", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="session", uselist=False, cascade="all, delete-orphan")

class SubTopic(Base):
    __tablename__ = "subtopics"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"))
    title = Column(String, nullable=False)
    status = Column(String, nullable=False) # pending/searching/verifying/done
    order_index = Column(Integer, nullable=False, default=0)
    
    # Relationships
    session = relationship("ResearchSession", back_populates="subtopics")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"), unique=True)
    markdown_content = Column(Text, nullable=True)
    metrics_json = Column(JSON, nullable=True) # e.g., {"word_count": int, "source_count": int, "time_taken": float}
    pdf_path = Column(String, nullable=True)
    ppt_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    session = relationship("ResearchSession", back_populates="report")

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"))
    subtopic_id = Column(String, ForeignKey("subtopics.id"), nullable=True)
    title = Column(String, nullable=True)
    url = Column(String, nullable=True)
    domain = Column(String, nullable=True)
    credibility_score = Column(Float, nullable=True)
    publish_date = Column(String, nullable=True)
    
    # Relationships
    session = relationship("ResearchSession", back_populates="sources")

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"))
    subtopic_id = Column(String, ForeignKey("subtopics.id"), nullable=True)
    content = Column(Text, nullable=True)
    confidence = Column(String, nullable=True)
    citations = Column(JSON, nullable=True) # List of source URLs or IDs
    
    # Relationships
    session = relationship("ResearchSession", back_populates="findings")
