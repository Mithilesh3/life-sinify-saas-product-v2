# Backend App

Canonical backend workspace for API and data work.

Run:

```powershell
cd D:\testing-life-signify\life-sinify-saas-product-v2\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
