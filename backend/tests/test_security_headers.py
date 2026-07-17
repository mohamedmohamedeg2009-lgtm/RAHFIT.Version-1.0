"""Tests for SecurityHeadersMiddleware.

Verifies that every response carries the expected defensive headers and
that the headers intentionally omitted (CSP, HSTS) are absent from
the FastAPI layer.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.middleware.security import SecurityHeadersMiddleware


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/ping")
    async def ping() -> JSONResponse:
        return JSONResponse({"ok": True})

    return TestClient(app, raise_server_exceptions=True)


def test_x_content_type_options_nosniff(client: TestClient) -> None:
    response = client.get("/ping")
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_x_frame_options_deny(client: TestClient) -> None:
    response = client.get("/ping")
    assert response.headers["X-Frame-Options"] == "DENY"


def test_referrer_policy(client: TestClient) -> None:
    response = client.get("/ping")
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_permissions_policy(client: TestClient) -> None:
    response = client.get("/ping")
    assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"


def test_csp_not_added_at_api_layer(client: TestClient) -> None:
    """CSP belongs on the frontend HTML document, not on JSON API responses.

    Asserting its absence here prevents accidental addition of an
    incomplete or incorrect policy at the wrong layer.
    """
    response = client.get("/ping")
    assert "Content-Security-Policy" not in response.headers


def test_hsts_not_added_over_plain_http(client: TestClient) -> None:
    """HSTS must not be injected by the FastAPI app.

    It must be set by the reverse proxy when TLS is terminated there,
    or it can break plain-HTTP development environments.
    """
    response = client.get("/ping")
    assert "Strict-Transport-Security" not in response.headers


def test_all_required_headers_present_on_every_response(client: TestClient) -> None:
    required = {
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Permissions-Policy",
    }
    response = client.get("/ping")
    missing = {h for h in required if h not in response.headers}
    assert not missing, f"Missing headers: {missing}"
