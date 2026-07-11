from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from licensly.client import Activation, Client
    from licensly.models import Lease


class LicenslySession:
    """Manages periodic heartbeats for an active Licensly client session."""

    def __init__(self, client: Client, activation: Activation) -> None:
        self._client = client
        self._session_token = activation.session_token
        self._lease = activation.lease
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    @property
    def lease(self) -> Lease:
        return self._lease

    @property
    def session_token(self) -> str:
        return self._session_token

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="licensly-heartbeat"
        )
        self._thread.start()

    def stop(self, deactivate: bool = True) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=15)
        if deactivate:
            try:
                self._client.deactivate(self._session_token)
            except Exception:
                pass

    def heartbeat(self, nonce: str | None = None) -> Lease:
        self._lease = self._client.heartbeat(self._session_token, nonce=nonce)
        return self._lease

    def _run(self) -> None:
        interval = self._lease.heartbeat_interval_seconds
        while not self._stop_event.wait(timeout=interval):
            try:
                self._lease = self._client.heartbeat(self._session_token)
                interval = self._lease.heartbeat_interval_seconds
            except Exception:
                pass

    def __enter__(self) -> LicenslySession:
        self.start()
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()
