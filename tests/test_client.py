from __future__ import annotations

import base64
import json
from typing import Any

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from licensly import Activation, AppVersionTooOldError, Client, ValidationResult


def signed_response() -> tuple[str, dict[str, Any]]:
    private_key = Ed25519PrivateKey.generate()
    public_key_hex = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()
    lease = {
        "product_id": "prd_test",
        "license_id": "lic_test",
        "license_status": "active",
        "session_id": "cls_test",
        "device_id_hash": "sha256-device-hash",
        "expires_at": "2026-07-12T14:00:00Z",
        "heartbeat_interval_seconds": 120,
        "offline_grace_seconds": 3600,
        "min_app_version": "2.0.0",
    }
    payload = base64.urlsafe_b64encode(
        json.dumps(lease, separators=(",", ":")).encode()
    ).rstrip(b"=").decode()
    envelope = {
        "version": 1,
        "kid": "key_test",
        "nonce": "nonce-test-01",
        "issued_at": "2026-07-12T13:00:00Z",
        "payload": payload,
    }
    signing_input = "\n".join(
        [
            "v1",
            envelope["kid"],
            envelope["nonce"],
            envelope["issued_at"],
            envelope["payload"],
        ]
    ).encode()
    envelope["signature"] = base64.urlsafe_b64encode(
        private_key.sign(signing_input)
    ).rstrip(b"=").decode()
    return public_key_hex, {
        "session_token": "session-token",
        "envelope": envelope,
    }


def test_validate_parses_unsigned_result_without_signature_verification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Client(
        "https://licenses.example",
        "prd_test",
        "not-used-for-sessionless-validation",
    )

    def fake_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
        assert path == "validate"
        assert payload == {
            "product_id": "prd_test",
            "license_key": "LIC-AAAA-BBBB-CCCC-DDDD-EEEE-FFFF-0000-1111",
            "device_id": "device-installation-8f27",
            "nonce": "nonce-validate-01",
            "app_version": "2.3.1",
            "issue_session": False,
        }
        return {
            "valid": True,
            "product_id": "prd_test",
            "license_id": "lic_test",
            "license_status": "active",
            "device_id_hash": "sha256-device-hash",
            "min_app_version": "2.0.0",
            "offline_usable": False,
        }

    monkeypatch.setattr(client, "_post", fake_post)
    result = client.validate(
        "LIC-AAAA-BBBB-CCCC-DDDD-EEEE-FFFF-0000-1111",
        "device-installation-8f27",
        nonce="nonce-validate-01",
        app_version="2.3.1",
    )

    assert isinstance(result, ValidationResult)
    assert result.valid is True
    assert result.license_id == "lic_test"
    assert result.offline_usable is False
    client.close()


def test_validate_with_session_verifies_and_unwraps_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    public_key_hex, response = signed_response()
    client = Client(
        "https://licenses.example",
        "prd_test",
        public_key_hex,
    )

    def fake_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
        assert path == "validate"
        assert payload["issue_session"] is True
        return response

    monkeypatch.setattr(client, "_post", fake_post)
    result = client.validate(
        "LIC-AAAA-BBBB-CCCC-DDDD-EEEE-FFFF-0000-1111",
        "device-installation-8f27",
        issue_session=True,
    )

    assert isinstance(result, Activation)
    assert result.session_token == "session-token"
    assert result.lease.product_id == "prd_test"
    client.close()


def test_activate_sends_optional_app_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    public_key_hex, response = signed_response()
    client = Client(
        "https://licenses.example",
        "prd_test",
        public_key_hex,
    )

    def fake_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
        assert path == "activate"
        assert payload["app_version"] == "2.3.1"
        return response

    monkeypatch.setattr(client, "_post", fake_post)
    result = client.activate(
        "LIC-AAAA-BBBB-CCCC-DDDD-EEEE-FFFF-0000-1111",
        "device-installation-8f27",
        app_version="2.3.1",
    )

    assert result.session_token == "session-token"
    client.close()


def test_app_version_too_old_error_mapping() -> None:
    client = Client("https://licenses.example", "prd_test", "unused")
    response = httpx.Response(
        403,
        json={
            "error": {
                "code": "app_version_too_old",
                "message": "Application version is below the product minimum.",
            }
        },
        request=httpx.Request("POST", "https://licenses.example/api/v1/validate"),
    )

    with pytest.raises(AppVersionTooOldError):
        client._raise_for_error(response)
    client.close()
