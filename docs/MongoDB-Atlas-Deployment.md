# MongoDB Atlas deployment

RAHFIT AI keeps the API and database private to the backend deployment. The React frontend must never receive a MongoDB URI, database credential, or Atlas secret.

## Backend environment variables

Set these values only in the backend hosting platform's secret/environment-variable settings:

```text
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-host>/?retryWrites=true&w=majority
MONGODB_DATABASE=rahfit
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
MONGODB_CONNECT_TIMEOUT_MS=10000
MONGODB_APP_NAME=rahfit-ai-api
```

`MONGODB_URI` and `MONGODB_DATABASE` are required. The timeout and application-name variables are optional and have the documented defaults. Keep TLS in the Atlas URI: `mongodb+srv://` enables the Atlas-compatible SRV/TLS connection flow.

If the Atlas password contains reserved URI characters such as `@`, `:`, `/`, `?`, `#`, `[`, or `]`, URL-encode it before placing it in the URI. For example, `@` becomes `%40`.

## Create Atlas safely

1. Create an Atlas project and an M0 or larger cluster suitable for the environment.
2. In **Database Access**, create a dedicated application database user. Use a strong, unique password and grant only the roles required by RAHFIT AI (normally `readWrite` for the application database).
3. In **Network Access**, allow only the egress IP addresses or private network of the backend hosting service. Do not leave `0.0.0.0/0` enabled after initial troubleshooting.
4. In Atlas, select **Connect** → **Drivers** and copy the `mongodb+srv://` connection-string template.
5. Replace placeholders locally only to test; store the final URI only in the backend host's secret manager.

## Test a connection before deployment

From PowerShell, set temporary process variables without committing them, then run the readiness script from `backend/`:

```powershell
$env:MONGODB_URI = "mongodb+srv://<username>:<password>@<cluster-host>/?retryWrites=true&w=majority"
$env:MONGODB_DATABASE = "rahfit"
$env:JWT_SECRET_KEY = "<existing-backend-jwt-secret>"
Set-Location backend
.\.venv\Scripts\python.exe scripts\verify_mongodb_atlas.py
```

The script pings MongoDB, prints the selected database name, initializes the existing application indexes, and verifies the required indexes. It never prints the URI or password. Startup uses the same ping and index-initialization lifecycle; failures report safe messages for missing configuration, authentication, DNS/SRV resolution, and unreachable databases.

## Migrate local data when credentials are available

Do not run these commands until the destination Atlas URI and network access are confirmed. From PowerShell:

```powershell
mongodump --uri "<LOCAL_MONGODB_URI>" --db "<LOCAL_DATABASE_NAME>" --archive="rahfit-backup.archive" --gzip
mongorestore --uri "<ATLAS_MONGODB_URI>" --archive="rahfit-backup.archive" --gzip --nsInclude="<LOCAL_DATABASE_NAME>.*"
```

If Atlas should use a different database name, use `--nsFrom` and `--nsTo` deliberately rather than restoring into an unintended namespace. Keep the generated archive outside Git and delete it securely after verification.

After restoring:

1. Compare collection names and document counts between local MongoDB and Atlas.
2. Run `scripts/verify_mongodb_atlas.py` against Atlas to verify ping and indexes.
3. Start the backend with the Atlas variables and call `/health`.
4. Validate representative users, soft-deleted records, workout data, assessments, nutrition plans, and AI conversations before changing production traffic.

## Incident response and boundaries

If a URI or password is exposed, revoke or rotate the Atlas database-user password immediately, update the backend host secret, and redeploy. Do not put `MONGODB_URI` in GitHub, `.env.example`, Vercel variables, Vite `VITE_*` variables, browser code, screenshots, or logs. Vercel hosts only the frontend; add the Atlas URI only to the separately deployed backend service.
