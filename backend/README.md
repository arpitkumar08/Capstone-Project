# ProcureIQ Backend

Django REST API using PostgreSQL for bid workspaces, document metadata, verification requests, reviewer decisions, and audit history.

## 1. Install PostgreSQL

On Windows, install the PostgreSQL server with the official [PostgreSQL Windows installer](https://www.postgresql.org/download/windows/). Remember the password you choose for the `postgres` administrator. The installer also includes pgAdmin.

## 2. Create an application role and database

In pgAdmin, connect to your local server, open **Tools → Query Tool**, and run:

```sql
CREATE USER procureiq_user WITH PASSWORD 'choose_a_local_password';
CREATE DATABASE procureiq OWNER procureiq_user;
```

Use a password you choose locally. Keep the database owned by the application role so Django can create and alter its tables during migrations.

## 3. Configure Django

In the `backend` folder, create a local `.env` from the example and replace the password:

```powershell
Copy-Item .env.example .env
```

The example connects to `127.0.0.1:5432`, database `procureiq`, as `procureiq_user`. `.env` is excluded from Git.

## 4. Install packages and create tables

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations procurement
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver 8000
```

The API base URL is `http://localhost:8000/api/v1`. The frontend reads `NEXT_PUBLIC_API_BASE_URL` from `frontend/.env.local`; set it to `http://localhost:8000/api/v1`. Endpoint details are in the [project README](../README.md).

## Storage and integrations

Bids, upload metadata, verification job requests, reviewer decisions, and audit events are stored in PostgreSQL. Uploaded file contents are validated then discarded; this step does not configure file storage. Verification requests are saved as queued records, but no worker runs them. Redis, AI, and authentication are still disabled.
