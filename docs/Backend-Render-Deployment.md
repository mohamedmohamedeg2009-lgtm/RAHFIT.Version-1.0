# Backend Deployment on Render

Deploy the FastAPI service separately from the Vercel frontend. The committed
`render.yaml` defines a Python 3.12 web service rooted at `backend/`, binds
Uvicorn to Render's dynamic `PORT`, and checks `/health` before routing traffic.

## Deploy

1. In Render, create a new Blueprint and select this repository. Render reads
   the root `render.yaml`.
2. Provide the prompted secret values in the Render Dashboard. Never copy a
   `.env` file or commit these values.
3. Deploy. When the service reports healthy, copy its public HTTPS URL.
4. Verify `https://<render-service-host>/health`. It must return
   `{"status":"ok","database":"ok"}`.
5. In Vercel, set `VITE_API_BASE_URL` for **Production** to
   `https://<render-service-host>`, then redeploy the frontend. The frontend adds `/api/v1`
   exactly once.

## Required Render environment variables

| Variable | Value |
| --- | --- |
| `MONGODB_URI` | Atlas connection URI, including the URL-encoded password. |
| `MONGODB_DATABASE` | Atlas database name, for example `rahfit_ai`. |
| `JWT_SECRET_KEY` | Existing production secret with at least 32 characters. |
| `ALLOWED_ORIGINS` | The exact stable Vercel Production Domain, for example `https://<your-stable-vercel-production-domain>`. |
| `APP_ENV` | `production` |
| `RAHFIT_DEBUG` | `false` |
| `LOG_LEVEL` | `INFO` |

Add optional existing variables only when their features are enabled, such as
`GOOGLE_CLIENT_ID` and AI provider keys. Do not set any
`VITE_*` variable on the backend, and never expose `MONGODB_URI` to Vercel or
browser code.

For Atlas setup and index verification, see
[MongoDB Atlas Deployment](MongoDB-Atlas-Deployment.md).

## Create an administrator

There is no Admin dashboard in the competition scope. Create or promote an
administrator only from a Render Shell (or a trusted local shell using the same
Atlas database):

```powershell
$env:ADMIN_EMAIL="admin@your-domain.example"
$env:ADMIN_PASSWORD="Choose-a-unique-strong-password-123"
python scripts/create_admin.py
```

The script never creates a default account, never prints the password, and
requires a password of at least 12 characters containing letters and numbers.
