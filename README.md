# OpenShelf MVP v1 (Backend PoC)

FastAPI + SQLite implementation for OpenShelf MVP v1.

## Features
- JWT authentication with bcrypt hashing
- Seeded SQLite mock data for USJ Spring 2026
- Listings CRUD/search filters
- Rule-based matching recommendations
- REST messaging flow (conversations + messages)
- Rule-based AI price recommendation

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open docs at: `http://127.0.0.1:8000/docs`

## Test
```bash
pytest -q
```

## End-to-end API walkthrough (Swagger)
1. `POST /api/auth/register`
2. `POST /api/auth/login`
3. Authorize with bearer token
4. `POST /api/listings`
5. `GET /api/listings` with filters
6. `GET /api/matches/recommendations`
7. `POST /api/conversations`
8. `POST /api/conversations/{id}/messages`
9. `GET /api/conversations/{id}/messages`
