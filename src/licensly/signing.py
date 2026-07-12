from __future__ import annotations

import base64
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

from licensly.exceptions import SignatureVerificationError
from licensly.models import Envelope, Lease


def _b64url_decode(s: str) -> bytes:
    """Decode base64url without padding."""
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def _build_signing_input(env: Envelope) -> bytes:
    """
    Canonical signing input per api/signing.md:
        v1\\n{kid}\\n{nonce}\\n{issued_at}\\n{payload}
    No trailing newline.
    """
    parts = [
        f"v{env.version}",
        env.kid,
        env.nonce,
        env.issued_at,
        env.payload,
    ]
    return "\n".join(parts).encode("utf-8")


def verify_envelope(envelope_dict: dict, public_key_hex: str) -> Lease:
    """
    Verify an Ed25519 envelope and return the decoded Lease.

    Raises SignatureVerificationError if the signature is invalid.
    Raises ValueError if the envelope or public key is malformed.
    """
    env = Envelope.from_dict(envelope_dict)

    public_key_bytes = bytes.fromhex(public_key_hex)
    public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)

    signing_input = _build_signing_input(env)
    sig_bytes = _b64url_decode(env.signature)

    try:
        public_key.verify(sig_bytes, signing_input)
    except InvalidSignature as exc:
        raise SignatureVerificationError(
            "Ed25519 signature verification failed"
        ) from exc

    payload_json = _b64url_decode(env.payload).decode("utf-8")
    lease_data = json.loads(payload_json)
    return Lease.from_dict(lease_data)
