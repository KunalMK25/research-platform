# Autonomous Agentic Research Platform

A full-stack web application where specialized AI agents autonomously plan, search, verify, synthesize, and generate professional research reports.

## Architecture

- **Frontend**: Next.js 14, Tailwind CSS, Framer Motion
- **Backend**: FastAPI
- **Database**: PostgreSQL / SQLite (via SQLAlchemy)
- **Vector DB**: ChromaDB
- **Agents**: Gemini API (planning, verifying, synthesizing, reporting)
- **Search**: Tavily API & arXiv API

## Setup Instructions

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### 3. Environment Variables

Create a `.env` file in the root directory based on `.env.example`:
- Add your `GEMINI_API_KEY`
- Add your `TAVILY_API_KEY`

### 4. Running the Application

**Run Backend (from `backend` folder):**
```bash
uvicorn main:app --reload --port 8000
```

**Run Frontend (from `frontend` folder):**
```bash
npm run dev
```

Visit `http://localhost:3000` to start researching!
