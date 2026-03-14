# life-sinify-saas-product-v2

Monorepo layout with clear separation:

- `frontend/` -> React + Vite app
- `backend/` -> FastAPI app
- `docker-compose.yml` -> local full stack orchestration
- `docs/TEAM_WORKFLOW.md` -> team collaboration workflow

Note: `frontend/` is the active UI workspace and should be treated as the source of truth for frontend changes.

## Quick Start

### Frontend

```powershell
cd D:\testing-life-signify\life-sinify-saas-product-v2
npm run frontend:install
npm run frontend:dev
```

### Backend

```powershell
cd D:\testing-life-signify\life-sinify-saas-product-v2\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker (Frontend + Backend + Postgres)

```powershell
cd D:\testing-life-signify\life-sinify-saas-product-v2
docker compose up --build
```
