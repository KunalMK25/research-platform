from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base

class ResearchSession(Base):
    __tablename__ = "research_sessions"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    topic = Column(String)
    depth = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    subtopics = relationship("SubTopic", back_populates="session", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="session", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="session", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="session", uselist=False, cascade="all, delete-orphan")

class SubTopic(Base):
    __tablename__ = "subtopics"
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"))
    title = Column(String)
    status = Column(String)
    
    session = relationship("ResearchSession", back_populates="subtopics")

class Source(Base):
    __tablename__ = "sources"
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"))
    subtopic_id = Column(String, ForeignKey("subtopics.id"), nullable=True)
    title = Column(String)
    url = Column(String)
    domain = Column(String)
    credibility_score = Column(Float)
    publish_date = Column(String, nullable=True)
    
    session = relationship("ResearchSession", back_populates="sources")

class Finding(Base):
    __tablename__ = "findings"
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"))
    subtopic_id = Column(String, ForeignKey("subtopics.id"), nullable=True)
    content = Column(Text)
    confidence = Column(String)
    citations = Column(JSON) # List of source URLs or IDs
    
    session = relationship("ResearchSession", back_populates="findings")

class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"))
    markdown_content = Column(Text)
    pdf_path = Column(String, nullable=True)
    ppt_path = Column(String, nullable=True)
    metrics_json = Column(JSON, nullable=True)
    
    session = relationship("ResearchSession", back_populates="report")
