import time
from typing import Any

import httpx
import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel


class GooglePayload(BaseModel):
    sub: str
    email: str
    email_verified: bool
    name: str | None = None


class GoogleTokenVerifier:
    def __init__(self, client_id: str | None) -> None:
        self.client_id = client_id
        self._certs_cache: dict[str, Any] = {}
        self._certs_cached_at: float = 0.0

    async def _get_google_certs(self) -> dict[str, Any]:
        now = time.time()
        # Cache for 1 hour to prevent flooding Google cert endpoints
        if not self._certs_cache or now - self._certs_cached_at > 3600:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://www.googleapis.com/oauth2/v3/certs")
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Failed to retrieve Google OAuth certificates.",
                    )
                self._certs_cache = response.json()
                self._certs_cached_at = now
        return self._certs_cache

    async def verify(self, id_token: str) -> GooglePayload:
        if not self.client_id:
            raise jwt.InvalidTokenError("Google client ID is not configured on the server.")
        try:
            # Unverified decode to extract header for kid
            unverified_header = jwt.get_unverified_header(id_token)
            kid = unverified_header.get("kid")
            if not kid:
                raise jwt.InvalidTokenError("Missing kid header in Google ID token.")

            certs = await self._get_google_certs()
            keys = certs.get("keys", [])
            jwk = next((k for k in keys if k.get("kid") == kid), None)
            if not jwk:
                raise jwt.InvalidTokenError("Matching public key not found for Google kid.")

            # Construct public key using PyJWT RSA helper
            from jwt.algorithms import RSAAlgorithm

            public_key: Any = RSAAlgorithm.from_jwk(jwk)

            # Decode and verify token signature, expiration, issuer, audience
            payload = jwt.decode(
                id_token,
                public_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=["https://accounts.google.com", "accounts.google.com"],
            )

            email = payload.get("email")
            email_verified = payload.get("email_verified")
            sub = payload.get("sub")

            if not email or not sub or email_verified is not True:
                raise jwt.InvalidTokenError(
                    "Google account email is not verified or subject is missing."
                )

            return GooglePayload(
                sub=sub,
                email=email,
                email_verified=email_verified,
                name=payload.get("name"),
            )
        except Exception as exc:
            raise jwt.InvalidTokenError(f"Google ID Token verification failed: {str(exc)}") from exc
