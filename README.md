# Verity AI — Multi-Agent Research Platform

Research anything. Trust everything.

A full-stack, production-grade autonomous research orchestration platform. Verity AI deploys a cooperative swarm of specialized AI agents that sequentially plan, search, verify, synthesize, and compile highly detailed professional research briefs with verified citations.

## Architecture

- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Framer Motion, ReactMarkdown
- **Backend**: FastAPI, Async SQLAlchemy, SQLite (via `aiosqlite`)
- **Vector Database**: ChromaDB
- **Agents Swarm**: Groq API (`llama-3.1-8b-instant` reasoning engine)
- **External Services**: Tavily Search API & arXiv Publications API
- **Document Exporters**: ReportLab (PDF) & Python-PPTX (Widescreen Presentation slides)
- **Authentication**: Firebase Client SDK (Google OAuth)

## Setup Instructions

### 1. Environment Configuration

Create a `.env` file in the root directory based on the included `.env.example`:
```bash
cp .env.example .env
```
Ensure you fill in your `GROQ_API_KEY`, `TAVILY_API_KEY`, and Firebase Web SDK keys.

### 2. Backend Installation & Setup

Navigate to the `backend` folder, set up your Python virtual environment, and install dependencies:
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # On Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

Initialize and seed mock database sessions (optional):
```bash
python seed.py
```

Start the FastAPI development server:
```bash
uvicorn main:app --reload --port 8000
```

### 3. Frontend Installation & Setup

Navigate to the `frontend` folder, install the package bundles, and start the Next.js development server:
```bash
cd ../frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to start researching!
