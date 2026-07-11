from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Lease:
    product_id: str
    license_id: str
    license_status: str
    session_id: str
    device_id_hash: str
    expires_at: str
    heartbeat_interval_seconds: int
    offline_grace_seconds: int
    min_app_version: str

    @classmethod
    def from_dict(cls, data: dict) -> "Lease":
        return cls(
            product_id=data["product_id"],
            license_id=data["license_id"],
            license_status=data["license_status"],
            session_id=data["session_id"],
            device_id_hash=data["device_id_hash"],
            expires_at=data["expires_at"],
            heartbeat_interval_seconds=int(data["heartbeat_interval_seconds"]),
            offline_grace_seconds=int(data["offline_grace_seconds"]),
            min_app_version=data.get("min_app_version", ""),
        )


@dataclass(frozen=True)
class Envelope:
    version: int
    kid: str
    nonce: str
    issued_at: str
    payload: str
    signature: str

    @classmethod
    def from_dict(cls, data: dict) -> "Envelope":
        return cls(
            version=int(data["version"]),
            kid=data["kid"],
            nonce=data["nonce"],
            issued_at=data["issued_at"],
            payload=data["payload"],
            signature=data["signature"],
        )
