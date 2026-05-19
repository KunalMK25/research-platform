from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import research, history, export
from database.db import engine, Base
import asyncio
app = FastAPI(title="Research Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(research.router, prefix="/api/research", tags=["Research"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

@app.get("/")
async def root():
    return {"message": "Research Platform API is running"}
