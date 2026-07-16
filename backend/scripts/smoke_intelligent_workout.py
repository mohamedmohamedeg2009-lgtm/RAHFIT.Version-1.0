"""Authenticated HTTP smoke journey for the RAHFIT Intelligent Workout API."""

from __future__ import annotations

import os
import sys
from typing import Any

import httpx


class SmokeFailure(RuntimeError):
    pass


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SmokeFailure(f"Required environment variable is missing: {name}")
    return value


def _profile() -> dict[str, Any]:
    return {
        "identity": {
            "full_name": "RAHFIT Smoke User",
            "age": 30,
            "gender": "male",
            "country": "EG",
        },
        "body": {"height_cm": 180.0, "weight_kg": 80.0, "body_fat_percentage": 18.0},
        "goals": {"primary_goal": "muscle_gain", "secondary_goal": "general_fitness"},
        "training": {
            "experience": "intermediate",
            "available_days": 3,
            "session_duration_minutes": 45,
            "available_equipment": ["bodyweight", "dumbbell"],
            "workout_location": "home_gym",
        },
        "lifestyle": {
            "sleep_hours": 8.0,
            "stress_level": 4,
            "activity_level": "moderate",
            "daily_water_ml": 2500,
        },
        "nutrition": {
            "dietary_preferences": [],
            "allergies": [],
            "dietary_restrictions": [],
        },
    }


def _health() -> dict[str, Any]:
    return {
        "injuries": [],
        "chronic_conditions": [],
        "pain_areas": [],
        "mobility_limitations": [],
        "surgery_history": [],
    }


class SmokeClient:
    def __init__(self, base_url: str) -> None:
        self.client = httpx.Client(base_url=base_url.rstrip("/"), timeout=30.0)

    def request(
        self,
        method: str,
        path: str,
        *,
        expected: int,
        headers: dict[str, str] | None = None,
        json: object | None = None,
    ) -> httpx.Response:
        response = self.client.request(method, path, headers=headers, json=json)
        if response.status_code != expected:
            request_id = response.headers.get("X-Request-ID", "unavailable")
            raise SmokeFailure(
                f"{method} {path} returned {response.status_code}; expected {expected}; "
                f"request_id={request_id}"
            )
        return response

    def authenticate(self, email: str, password: str) -> dict[str, str]:
        registration = self.client.post(
            "/api/v1/auth/register", json={"email": email, "password": password}
        )
        if registration.status_code == 201:
            payload = registration.json()
        elif registration.status_code == 409:
            payload = self.request(
                "POST",
                "/api/v1/auth/login",
                expected=200,
                json={"email": email, "password": password},
            ).json()
        else:
            raise SmokeFailure(
                f"Authentication setup failed with status {registration.status_code}."
            )
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise SmokeFailure("Authentication response did not contain an access token.")
        return {"Authorization": f"Bearer {token}"}

    def close(self) -> None:
        self.client.close()


def _step(number: int, message: str) -> None:
    print(f"[{number:02d}] {message}")


def run() -> None:
    base_url = os.getenv("RAHFIT_API_BASE_URL", "http://127.0.0.1:8000")
    primary_email = _required("RAHFIT_SMOKE_EMAIL")
    primary_password = _required("RAHFIT_SMOKE_PASSWORD")
    secondary_email = _required("RAHFIT_SMOKE_SECONDARY_EMAIL")
    secondary_password = _required("RAHFIT_SMOKE_SECONDARY_PASSWORD")
    if primary_email.lower() == secondary_email.lower():
        raise SmokeFailure("Primary and secondary smoke-test accounts must be different.")

    api = SmokeClient(base_url)
    try:
        primary = api.authenticate(primary_email, primary_password)
        secondary = api.authenticate(secondary_email, secondary_password)
        _step(1, "Authenticated both isolated smoke-test users.")

        api.request("PUT", "/api/v1/profile", expected=204, headers=primary, json=_profile())
        api.request("PUT", "/api/v1/health-profile", expected=204, headers=primary, json=_health())
        _step(2, "Stored the canonical profile and explicit health declaration.")

        generated = api.request(
            "POST",
            "/api/v1/intelligent-workouts/plans/generate",
            expected=201,
            headers=primary,
            json={"duration_weeks": 8, "use_ai_assistance": False},
        ).json()
        if generated.get("generation_mode") != "deterministic":
            raise SmokeFailure("Expected deterministic generation mode.")
        plan_id = generated["plan_id"]
        _step(3, "Generated and validated a deterministic intelligent workout plan.")

        active = api.request(
            "GET", "/api/v1/intelligent-workouts/plans/active", expected=200, headers=primary
        ).json()
        history = api.request(
            "GET", "/api/v1/intelligent-workouts/plans", expected=200, headers=primary
        ).json()
        detail = api.request(
            "GET",
            f"/api/v1/intelligent-workouts/plans/{plan_id}",
            expected=200,
            headers=primary,
        ).json()
        if active.get("plan_id") != plan_id or not history.get("items") or detail != generated:
            raise SmokeFailure("Plan retrieval did not match the generated plan.")
        _step(4, "Verified active plan, plan history, and plan detail contracts.")

        api.request(
            "GET",
            f"/api/v1/intelligent-workouts/plans/{plan_id}",
            expected=404,
            headers=secondary,
        )
        _step(5, "Verified cross-user plan isolation.")

        day = generated["weekly_schedule"][0]
        exercise = day["sections"][0]["exercises"][0]
        session = api.request(
            "POST",
            "/api/v1/intelligent-workouts/sessions",
            expected=201,
            headers=primary,
            json={
                "plan_id": plan_id,
                "day_number": day["day_number"],
                "status": "in_progress",
                "completed_exercises": [],
            },
        ).json()
        session_id = session["session_id"]
        api.request(
            "GET",
            f"/api/v1/intelligent-workouts/sessions/{session_id}",
            expected=200,
            headers=primary,
        )
        api.request(
            "GET",
            f"/api/v1/intelligent-workouts/sessions/{session_id}",
            expected=404,
            headers=secondary,
        )
        _step(6, "Started, retrieved, and ownership-checked a workout session.")

        progress: dict[str, Any] = {
            "status": "in_progress",
            "completed_exercises": [
                {
                    "exercise_id": exercise["exercise_id"],
                    "completed_sets": [{"set_number": 1, "actual_reps": 8, "completed": True}],
                    "skipped": False,
                    "pain_reported": False,
                }
            ],
            "actual_duration_minutes": 20,
        }
        updated = api.request(
            "PATCH",
            f"/api/v1/intelligent-workouts/sessions/{session_id}",
            expected=200,
            headers=primary,
            json=progress,
        ).json()
        if not 0 < updated.get("completion_percentage", 0) < 100:
            raise SmokeFailure("Server-side completion calculation was not observed.")
        _step(7, "Verified server-owned session progress calculation.")

        progress["completed_exercises"][0]["pain_reported"] = True
        progress["completed_exercises"][0]["pain_area"] = "shoulder discomfort"
        pain = api.request(
            "PATCH",
            f"/api/v1/intelligent-workouts/sessions/{session_id}",
            expected=200,
            headers=primary,
            json=progress,
        ).json()
        if "pain_requires_review" not in pain.get("adaptation_flags", []):
            raise SmokeFailure("Pain review flag was not produced.")
        _step(8, "Verified deterministic pain review signaling.")

        before = api.request(
            "GET",
            f"/api/v1/intelligent-workouts/plans/{plan_id}",
            expected=200,
            headers=primary,
        ).json()
        recommendation = api.request(
            "POST",
            "/api/v1/intelligent-workouts/adaptation/analyze",
            expected=200,
            headers=primary,
            json={"plan_id": plan_id},
        ).json()
        after = api.request(
            "GET",
            f"/api/v1/intelligent-workouts/plans/{plan_id}",
            expected=200,
            headers=primary,
        ).json()
        if recommendation.get("automatic_application_allowed") or before != after:
            raise SmokeFailure("Adaptation analysis mutated the plan or allowed automatic use.")
        _step(9, "Verified non-mutating adaptation analysis.")

        progress["status"] = "completed"
        api.request(
            "PATCH",
            f"/api/v1/intelligent-workouts/sessions/{session_id}",
            expected=200,
            headers=primary,
            json=progress,
        )
        api.request(
            "POST",
            f"/api/v1/intelligent-workouts/plans/{plan_id}/archive",
            expected=200,
            headers=primary,
        )
        _step(10, "Completed the session and archived the smoke-test plan safely.")
    finally:
        api.close()


def main() -> int:
    try:
        run()
    except (SmokeFailure, httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
        print(f"SMOKE TEST FAILED: {exc}", file=sys.stderr)
        return 1
    print("INTELLIGENT WORKOUT SMOKE TEST: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
