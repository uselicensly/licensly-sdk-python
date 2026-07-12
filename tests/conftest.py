"""Pytest fixtures and helpers for licensly-sdk-python tests."""
from __future__ import annotations

import json
import pathlib

import pytest

FIXTURES_DIR = pathlib.Path(__file__).parent.parent / ".contract" / "fixtures"


def load_fixture(name: str) -> dict:
    path = FIXTURES_DIR / name
    if not path.is_file():
        raise FileNotFoundError(
            f"missing {path}; run ./scripts/fetch-contract.sh first"
        )
    return json.loads(path.read_text())


@pytest.fixture
def valid_fixture() -> dict:
    return load_fixture("ed25519_valid.json")


@pytest.fixture
def mutated_payload_fixture() -> dict:
    return load_fixture("ed25519_mutated_payload.json")


@pytest.fixture
def bad_signature_fixture() -> dict:
    return load_fixture("ed25519_bad_signature.json")
