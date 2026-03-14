# Team Workflow (Frontend + Backend)

## Repo Structure

- `frontend/`: React + Vite app (UI, pages, components, frontend services)
- `backend/`: FastAPI app (APIs, DB models, business logic)
- `docker-compose.yml`: local full-stack orchestration
- `tests/`: backend-oriented tests

## Daily Commands

### Frontend Developer

```powershell
cd D:\testing-life-signify\life-sinify-saas-product-v2
npm run frontend:install
npm run frontend:dev
```

### Backend Developer

```powershell
cd D:\testing-life-signify\life-sinify-saas-product-v2\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Full Stack in Dev (Docker)

```powershell
cd D:\testing-life-signify\life-sinify-saas-product-v2
docker compose up --build
```

## Safe Collaboration Rules

1. Frontend work should only change files inside `frontend/` unless API contract changes are required.
2. Backend work should only change files inside `backend/` unless contract docs need updates.
3. Any API request/response change must be documented in PR description and reflected in frontend service layer.
4. Keep shared env keys in root `.env` and frontend-only Vite keys in `frontend/.env`.
5. Prefer feature branches:
   - `frontend/<feature-name>`
   - `backend/<feature-name>`

## Integration Handshake

When wiring frontend to backend:

1. Backend developer publishes endpoint + payload contract.
2. Frontend developer updates `frontend/src/services/*` first.
3. UI changes are done only after service integration is validated.
4. Verify with:
   - `GET /health`
   - auth flow
   - one protected API call
