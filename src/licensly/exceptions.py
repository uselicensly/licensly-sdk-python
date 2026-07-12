from __future__ import annotations


class LicenslyError(Exception):
    """Base class for all Licensly SDK errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class InvalidRequestError(LicenslyError):
    """400: Malformed JSON, missing fields, or bad nonce."""


class InvalidLicenseError(LicenslyError):
    """401: Unknown key, revoked license, banned device, or bad session."""


class ActivationLimitError(LicenslyError):
    """403: Activation slot cap exceeded."""


class SessionLimitError(LicenslyError):
    """403: Concurrent client session cap exceeded."""


class AppVersionTooOldError(LicenslyError):
    """403: Client app version is below the product minimum."""


class PlanLimitError(LicenslyError):
    """403: Organization service-plan resource cap exceeded."""


class RateLimitedError(LicenslyError):
    """429: IP / product / key-prefix throttle triggered."""


class ServerError(LicenslyError):
    """500: Unexpected server failure."""


class SignatureVerificationError(LicenslyError):
    """Ed25519 envelope signature verification failed."""
