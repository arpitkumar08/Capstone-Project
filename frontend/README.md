# ProcureIQ Frontend

Next.js frontend for the GeM bid compliance workspace. It connects to the Django REST API through `NEXT_PUBLIC_API_BASE_URL`.

## Run locally

```powershell
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). `/login` is a demo screen and does not authenticate users.

Without `NEXT_PUBLIC_API_BASE_URL`, the frontend falls back to the local Next.js API routes under `/api`.

## Production build

```powershell
npm run build
npm start
```
