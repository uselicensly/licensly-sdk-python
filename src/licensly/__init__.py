"""Licensly Client API SDK for Python."""

from .client import Activation, Client
from .exceptions import (
    ActivationLimitError,
    InvalidLicenseError,
    InvalidRequestError,
    LicenslyError,
    RateLimitedError,
    ServerError,
    SessionLimitError,
    SignatureVerificationError,
)
from .models import Envelope, Lease
from .session import LicenslySession
from .signing import verify_envelope

__all__ = [
    "Activation",
    "ActivationLimitError",
    "Client",
    "Envelope",
    "InvalidLicenseError",
    "InvalidRequestError",
    "Lease",
    "LicenslyError",
    "LicenslySession",
    "RateLimitedError",
    "ServerError",
    "SessionLimitError",
    "SignatureVerificationError",
    "verify_envelope",
]
__version__ = "0.1.0"
