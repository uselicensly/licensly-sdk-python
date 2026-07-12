"""Golden fixture signing verification tests.

These tests exercise licensly.signing.verify_envelope against the canonical
golden vectors from fixtures/. They require no network access.
"""
from __future__ import annotations

import pytest

from licensly.signing import verify_envelope
from licensly.exceptions import SignatureVerificationError


class TestGoldenVerify:
    def test_valid_envelope_returns_lease(self, valid_fixture):
        public_key_hex = valid_fixture["public_key_hex"]
        lease = verify_envelope(valid_fixture["envelope"], public_key_hex)
        assert lease.license_status == "active"
        assert lease.product_id == "prd_golden"
        assert lease.session_id == "cls_golden"
        assert lease.heartbeat_interval_seconds == 120
        assert lease.offline_grace_seconds == 3600

    def test_mutated_payload_raises(self, mutated_payload_fixture):
        public_key_hex = mutated_payload_fixture["public_key_hex"]
        with pytest.raises(SignatureVerificationError):
            verify_envelope(mutated_payload_fixture["envelope"], public_key_hex)

    def test_bad_signature_raises(self, bad_signature_fixture):
        public_key_hex = bad_signature_fixture["public_key_hex"]
        with pytest.raises(SignatureVerificationError):
            verify_envelope(bad_signature_fixture["envelope"], public_key_hex)

    def test_wrong_public_key_raises(self, valid_fixture):
        wrong_key = "a" * 64
        with pytest.raises(Exception):
            verify_envelope(valid_fixture["envelope"], wrong_key)
