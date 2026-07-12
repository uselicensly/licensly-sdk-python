"""Licensly Client API SDK for Python."""

from .client import Activation, Client
from .exceptions import (
    ActivationLimitError,
    AppVersionTooOldError,
    InvalidLicenseError,
    InvalidRequestError,
    LicenslyError,
    PlanLimitError,
    RateLimitedError,
    ServerError,
    SessionLimitError,
    SignatureVerificationError,
)
from .models import Envelope, Lease, ValidationResult
from .session import LicenslySession
from .signing import verify_envelope

__all__ = [
    "Activation",
    "ActivationLimitError",
    "AppVersionTooOldError",
    "Client",
    "Envelope",
    "InvalidLicenseError",
    "InvalidRequestError",
    "Lease",
    "LicenslyError",
    "LicenslySession",
    "PlanLimitError",
    "RateLimitedError",
    "ServerError",
    "SessionLimitError",
    "SignatureVerificationError",
    "ValidationResult",
    "verify_envelope",
]
__version__ = "0.1.0"
