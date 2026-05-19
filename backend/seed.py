import asyncio
from database.db import AsyncSessionLocal, engine, Base
from database.models import ResearchSession, SubTopic, Source, Finding, Report
from datetime import datetime, timedelta
import uuid
import json

async def seed_db():
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as db:
        # Create a mock session 1
        session_id_1 = str(uuid.uuid4())
        session1 = ResearchSession(
            id=session_id_1,
            user_id="anonymous",
            topic="The Impact of AGI on Global Economics",
            depth="Deep",
            status="completed",
            created_at=datetime.utcnow() - timedelta(days=2),
            completed_at=datetime.utcnow() - timedelta(days=2, hours=-1)
        )
        db.add(session1)
        
        st_id = str(uuid.uuid4())
        db.add(SubTopic(id=st_id, session_id=session_id_1, title="Automation", status="completed"))
        
        report_md_1 = """# Executive Summary
AGI is expected to drastically alter global economics.

# Findings
## Subtopic 1
AGI introduces hyper-automation. [Source: https://example.com/agi]

# Contradictions
None

# References
- https://example.com/agi"""

        db.add(Report(
            id=str(uuid.uuid4()),
            session_id=session_id_1,
            markdown_content=report_md_1,
            metrics_json={"citation_coverage": 100, "source_diversity": 1, "contradiction_rate": 0, "depth_score": 10}
        ))
        
        # Create a mock session 2 (Running)
        session_id_2 = str(uuid.uuid4())
        session2 = ResearchSession(
            id=session_id_2,
            user_id="anonymous",
            topic="Next-Gen Solid State Batteries",
            depth="Standard",
            status="running",
            created_at=datetime.utcnow() - timedelta(minutes=5)
        )
        db.add(session2)

        await db.commit()
        print(f"Mock data seeded! You can view these in the history page.")

if __name__ == "__main__":
    asyncio.run(seed_db())
