"""
Navelle AI Module — Backend Client
Fetches real user health data from the Navelle REST API.

The single key endpoint is:
    GET /api/users/{user_id}/health-overview?days=7&limit=10

Response schema:
{
    "user": { user_id, name, email, dob, health_condition },
    "symptoms": [{ _id, symptom_name, severity_level, timestamp, notes }],
    "menstrual_trackers": [{ _id, start_date, end_date, flow_intensity, variation, timestamp }],
    "lab_histories": [...],
    "medical_histories": [{ _id, condition, category, date_diagnosed, started_problem, notes }],
    "chat_messages": [...]
}
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from ai.config import settings

logger = logging.getLogger(__name__)

# Default window for health data
DEFAULT_DAYS = 30
DEFAULT_LIMIT = 50


class BackendClientError(Exception):
    """Raised when the backend returns an unexpected error."""


class BackendAuthError(BackendClientError):
    """Raised when the backend returns 401 Unauthorized."""


class BackendClient:
    """Async HTTP client for the Navelle backend REST API."""

    def __init__(self) -> None:
        self._base_url = settings.backend_url.rstrip("/")
        self._customer_token = settings.customer_token
        self._admin_token = settings.admin_token
        self._timeout = httpx.Timeout(15.0)

    # ── internal helpers ───────────────────────────────────────────────────────

    def _customer_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._customer_token:
            headers["Authorization"] = self._customer_token
        return headers

    def _admin_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._admin_token:
            headers["Authorization"] = self._admin_token
        return headers

    async def _get(self, path: str, params: dict | None = None, admin: bool = False) -> Any:
        """Perform a GET request and return the parsed JSON body."""
        url = f"{self._base_url}{path}"
        headers = self._admin_headers() if admin else self._customer_headers()
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                resp = await client.get(url, headers=headers, params=params)
            except httpx.RequestError as exc:
                logger.error("Backend request failed: %s", exc)
                raise BackendClientError(f"Network error contacting backend: {exc}") from exc

            if resp.status_code == 401:
                logger.warning("Backend returned 401 for %s", url)
                raise BackendAuthError("Backend authentication failed (401). Check your token.")
            if resp.status_code == 404:
                logger.warning("Backend 404 for %s — returning empty dict", url)
                return {}
            if resp.status_code >= 500:
                logger.error("Backend 5xx for %s: %s", url, resp.text[:300])
                raise BackendClientError(f"Backend server error ({resp.status_code})")

            try:
                return resp.json()
            except Exception as exc:
                logger.error("Failed to parse backend response: %s", exc)
                return {}

    async def _graphql(self, query: str, variables: dict, admin: bool = False) -> Any:
        """Execute a GraphQL query and return response data."""
        url = f"{self._base_url}/graphql"
        headers = self._admin_headers() if admin else self._customer_headers()
        payload = {"query": query, "variables": variables}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
            except httpx.RequestError as exc:
                logger.error("GraphQL request failed: %s", exc)
                raise BackendClientError(f"Network error: {exc}") from exc

            if resp.status_code == 401:
                raise BackendAuthError("GraphQL authentication failed (401).")
            if resp.status_code >= 500:
                raise BackendClientError(f"GraphQL server error ({resp.status_code})")

            body = resp.json()
            if "errors" in body:
                logger.warning("GraphQL errors: %s", body["errors"])
            return body.get("data", {})

    # ── public methods ─────────────────────────────────────────────────────────

    async def get_user_health_overview(
        self,
        user_id: str,
        days: int = DEFAULT_DAYS,
        limit: int = DEFAULT_LIMIT,
    ) -> dict:
        """
        Fetch comprehensive health data for a user.

        Returns a dict with keys:
            user, symptoms, menstrual_trackers, medical_histories,
            lab_histories, chat_messages, files
        Falls back to an empty-data structure on any error so callers
        can still function without crashing.
        """
        path = f"/api/users/{user_id}/health-overview"
        params = {"days": days, "limit": limit}
        try:
            data = await self._get(path, params=params)
            logger.info("Health overview for user %s: %s", user_id, list(data.keys()))
            # Normalise: ensure all expected keys exist
            return {
                "user": data.get("user", {}),
                "symptoms": data.get("symptoms", []),
                "menstrual_trackers": data.get("menstrual_trackers", []),
                "medical_histories": data.get("medical_histories", []),
                "lab_histories": data.get("lab_histories", []),
                "chat_messages": data.get("chat_messages", []),
                "files": data.get("files", []),  # Cloudinary files
            }
        except BackendAuthError:
            logger.error("Auth error fetching health overview for user %s", user_id)
            return _empty_health_data(user_id)
        except BackendClientError as exc:
            logger.error("Backend error fetching health overview: %s", exc)
            return _empty_health_data(user_id)

    async def get_customer_profile(self, user_id: str) -> dict:
        """
        Fetch extended customer profile via GraphQL (pauseType, topics, etc.).
        Uses ADMIN_TOKEN.
        """
        query = """
        query customer($id: String!) {
            customer(id: $id) {
                id email username role status
                customer {
                    id fullName dob gender bloodGroup
                    pauseType symptomTypes topics planName
                }
            }
        }
        """
        try:
            data = await self._graphql(query, {"id": user_id}, admin=True)
            return data.get("customer", {})
        except (BackendAuthError, BackendClientError) as exc:
            logger.error("Error fetching customer profile for %s: %s", user_id, exc)
            return {}

    async def get_user_files(self, user_id: str) -> list[dict]:
        """
        Fetch user's uploaded files from the backend.
        Returns files collection with Cloudinary URLs.

        Expected response format:
        [
            {
                "_id": "...",
                "url": "https://res.cloudinary.com/...",
                "name": "Laboratory_Test_Report.pdf",
                "type": "DOC",
                "createdAt": "...",
                "postId": "..."
            }
        ]
        """
        # Try different possible endpoints
        endpoints_to_try = [
            f"/api/users/{user_id}/files",
            f"/api/customers/{user_id}/files",
            f"/api/files/user/{user_id}",
        ]

        for path in endpoints_to_try:
            try:
                logger.info("Trying endpoint: %s", path)
                data = await self._get(path)

                # Log raw response for debugging
                logger.info("Response from %s: %s", path, type(data))

                if isinstance(data, list):
                    logger.info("Found %d files from %s", len(data), path)
                    return data
                elif isinstance(data, dict):
                    files = data.get("files", [])
                    logger.info("Found %d files from %s (in 'files' key)", len(files), path)
                    return files

            except BackendAuthError:
                logger.warning("Auth error for %s", path)
                continue
            except BackendClientError as exc:
                logger.warning("Error for %s: %s", path, exc)
                continue

        logger.error("All endpoints failed for user %s", user_id)
        return []


# ── Helpers ────────────────────────────────────────────────────────────────────

def _empty_health_data(user_id: str) -> dict:
    """Return a safe empty health-data dict when the backend is unreachable."""
    return {
        "user": {"user_id": user_id, "name": "Unknown", "email": "", "dob": None, "health_condition": "NONE"},
        "symptoms": [],
        "menstrual_trackers": [],
        "medical_histories": [],
        "lab_histories": [],
        "chat_messages": [],
    }


# ── Singleton ──────────────────────────────────────────────────────────────────
backend_client = BackendClient()
