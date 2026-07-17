# Production-Grade Authentication Upgrade (Google Sign-In & Password Reset)

This document describes the design, implementation, and verification steps of the authentication upgrade, adding professional Google Identity Services authentication and a secure Forgot/Reset Password flow.

---

## 1. Google Sign-in Authentication Flow
The Google Authentication flow uses the official **Google Identity Services** JS SDK on the frontend and custom **OpenID Connect (OIDC)** validation on the backend.

### A. Frontend Flow
- A Google Sign-In button is rendered on the `LoginPage` and `RegisterPage` when `VITE_GOOGLE_CLIENT_ID` is set in the environment variables.
- Upon successful user interaction, Google returns a cryptographically signed JSON Web Token (JWT) credential (ID token).
- This token is sent to the backend `/api/v1/auth/google` POST endpoint.

### B. Backend Flow
- The `GoogleTokenVerifier` validates the token dynamically using Google's public JSON Web Keys (JWKS).
- The verifier validates:
  1. Token expiration (`exp`).
  2. The target client audience matches the configured `GOOGLE_CLIENT_ID`.
  3. The issuer (`iss`) matches Google.
  4. The email is verified by Google (`email_verified` is `True`).
- To prevent unnecessary certificate network calls, the Google OIDC public key certificates are cached in memory for **1 hour**.

### C. Account Linking Policy
When a valid ID token is verified:
1. We query the database for a user matching `provider="google"` and `provider_subject` (the unique Google user ID).
2. If found, the user is signed in directly.
3. If not found, we look up a user with a matching `email`.
   - If a matching email exists, is active, and is not linked to another provider, we link the Google account details to this existing user (sets `provider="google"`, `provider_subject`, `verified_email`).
   - If the email matches but is already linked to another provider, authentication is rejected with a generic security error.
4. If no user exists, we create a new user account with locked empty local passwords (`provider="google"`, `provider_subject`, `verified_email`, `password_hash=""`).

---

## 2. Forgot / Reset Password Flow
The Forgot/Reset Password flow is designed to prevent user enumeration and ensure token security.

### A. Forgot Password
- Users request a password reset link by entering their email address on the `/forgot-password` page.
- The backend `/api/v1/auth/forgot-password` endpoint generates a secure, cryptographically random `urlsafe` token.
- The plaintext token is **never stored**. Only a **SHA-256 hash** of the token is stored in the `password_resets` collection alongside the user ID, creation date, and expiration time.
- The endpoint **always returns a generic response** (e.g., "If an account exists, a reset link has been sent") to prevent user email enumeration.

### B. Reset Password
- Clicking the email link navigates to `/reset-password?token=TOKEN`.
- The user inputs their new password (validated client-side to require **at least 12 characters** and a matching confirmation).
- The backend `/api/v1/auth/reset-password` endpoint performs the following atomic operations:
  1. Hashes the received plaintext token using SHA-256.
  2. Queries the `password_resets` collection for an active, unused, unexpired token matching the hash.
  3. Mark the token as **used** immediately (single-use validation).
  4. Updates the user's password hash.
  5. **Global Session Revocation**: Atomically increments the user's `token_version` in the database. Since current active JWT payloads are validated against the user's database `token_version` on every request, this immediately invalidates all active user sessions globally.

---

## 3. Email Delivery Integration
The backend exposes a provider-neutral `EmailService` supporting:
- **Development/Test Mode**: When `EMAIL_PROVIDER=development`, emails are not sent. Instead, the branded HTML message containing the password reset URL is output directly to the backend terminal logs for safe development testing.
- **Production Mode**: When `EMAIL_PROVIDER=smtp`, the email service establishes a secure connection to the SMTP server (using TLS/STARTTLS) to deliver professionally styled, branded RAHFIT AI emails with a plain-text fallback.

---

## 4. Database Schema & Indexes
To support OAuth account details, the `User` model is extended with:
- `provider`: String, e.g. `"google"`
- `provider_subject`: String (Google user sub)
- `verified_email`: String (Google verified email address)
- `token_version`: Integer (for global session revocation)

### Migration-safe Indexes
The following indexes are initialized dynamically on startup:
1. **Unique Index**: On `(provider, provider_subject)` where `is_active: True`.
2. **Unique Index**: On `token_hash` in `password_resets` collection.
3. **TTL Automatic Index**: On `expires_at` in `password_resets` collection to automatically clean up expired tokens.

---

## 5. Verification Gates
To verify all operations, both backend and frontend quality checks were executed.

### Backend Tests
- Pytest cases check OIDC claims, safe account linking, SHA-256 hashing, token deactivations, TTL config, and generic error verification.
```powershell
pytest backend/tests/test_auth_upgrade.py
```
- Linting and static analysis:
```powershell
ruff check backend
black --check backend
mypy --strict backend/app
```

### Frontend Tests
- Vitest suite covers Google Sign-In button rendering, forgot/reset validation fields, and API request handling.
```powershell
npm run test
npm run lint
npm run build
```
