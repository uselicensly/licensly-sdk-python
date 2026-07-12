from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Any

import httpx

from licensly.exceptions import (
    ActivationLimitError,
    AppVersionTooOldError,
    InvalidLicenseError,
    InvalidRequestError,
    LicenslyError,
    PlanLimitError,
    RateLimitedError,
    ServerError,
    SessionLimitError,
)
from licensly.models import Lease, ValidationResult
from licensly.session import LicenslySession
from licensly.signing import verify_envelope

_DEFAULT_TIMEOUT = 10.0

_ERROR_MAP: dict[str, type[LicenslyError]] = {
    "invalid_request": InvalidRequestError,
    "invalid_license": InvalidLicenseError,
    "activation_limit": ActivationLimitError,
    "session_limit": SessionLimitError,
    "app_version_too_old": AppVersionTooOldError,
    "plan_limit": PlanLimitError,
    "rate_limited": RateLimitedError,
    "internal": ServerError,
}


@dataclass(frozen=True)
class Activation:
    """Result of a successful activate call."""

    session_token: str
    lease: Lease


class Client:
    """Synchronous Licensly Client API client.

    Device IDs are caller-supplied — this SDK never auto-collects HWID.
    """

    def __init__(
        self,
        base_url: str,
        product_id: str,
        public_key_hex: str,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._product_id = product_id
        self._public_key_hex = public_key_hex
        self._http = httpx.Client(timeout=timeout)

    def _url(self, path: str) -> str:
        return f"{self._base_url}/api/v1/{path.lstrip('/')}"

    def _raise_for_error(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        try:
            body = response.json()
            code = body.get("error", {}).get("code", "internal")
            message = body.get("error", {}).get("message", "Unknown error")
        except Exception:
            code = "internal"
            message = response.text or "Unknown error"
        raise _ERROR_MAP.get(code, LicenslyError)(message, code=code)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._http.post(
            self._url(path),
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        self._raise_for_error(response)
        return response.json()

    def _lease_from_signed(self, data: dict[str, Any]) -> Lease:
        envelope = data.get("envelope", data)
        return verify_envelope(envelope, self._public_key_hex)

    def _activation_from_signed(self, data: dict[str, Any]) -> Activation:
        token = data.get("session_token")
        if not token:
            raise LicenslyError(
                "signed response missing session_token", code="internal"
            )
        return Activation(session_token=token, lease=self._lease_from_signed(data))

    def activate(
        self,
        license_key: str,
        device_id: str,
        nonce: str | None = None,
        app_version: str | None = None,
    ) -> Activation:
        payload = {
            "license_key": license_key,
            "product_id": self._product_id,
            "device_id": device_id,
            "nonce": nonce or secrets.token_hex(16),
        }
        if app_version is not None:
            payload["app_version"] = app_version
        data = self._post(
            "activate",
            payload,
        )
        return self._activation_from_signed(data)

    def heartbeat(self, session_token: str, nonce: str | None = None) -> Lease:
        return self._lease_from_signed(
            self._post(
                "heartbeat",
                {
                    "session_token": session_token,
                    "product_id": self._product_id,
                    "nonce": nonce or secrets.token_hex(16),
                },
            )
        )

    def validate(
        self,
        license_key: str,
        device_id: str,
        nonce: str | None = None,
        app_version: str | None = None,
        issue_session: bool = False,
    ) -> ValidationResult | Activation:
        payload = {
            "license_key": license_key,
            "product_id": self._product_id,
            "device_id": device_id,
            "nonce": nonce or secrets.token_hex(16),
            "issue_session": issue_session,
        }
        if app_version is not None:
            payload["app_version"] = app_version
        data = self._post("validate", payload)
        if issue_session:
            return self._activation_from_signed(data)
        return ValidationResult.from_dict(data)

    def deactivate(self, session_token: str, nonce: str | None = None) -> None:
        self._post(
            "deactivate",
            {
                "session_token": session_token,
                "product_id": self._product_id,
                "nonce": nonce or secrets.token_hex(16),
            },
        )

    def session(self, activation: Activation) -> LicenslySession:
        return LicenslySession(client=self, activation=activation)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
