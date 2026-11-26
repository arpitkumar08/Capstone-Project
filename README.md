# ProcureIQ GeM Bid Compliance

The project is split into two applications:

- [`frontend/`](frontend/README.md) — Next.js web application
- [`backend/`](backend/README.md) — Django REST API with PostgreSQL persistence

## Local setup

1. Install PostgreSQL using the [official Windows installer](https://www.postgresql.org/download/windows/).
2. Create a local PostgreSQL role and database as described in [backend setup](backend/README.md).
3. Copy `backend/.env.example` to `backend/.env` and set your local database password.
4. In a PowerShell terminal, initialize and run the backend:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations procurement
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver 8000
```

5. In a second terminal, configure and run the frontend:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1` in `frontend/.env.local` to use Django and PostgreSQL.

Redis, AI, authentication, and background processing remain disabled. Uploaded file metadata is stored in PostgreSQL; file contents are not retained.
