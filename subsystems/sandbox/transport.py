"""Transport helpers for worker/host communication."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from multiprocessing.connection import Client, Connection, Listener
from typing import Any


@dataclass
class HostTransport:
    """Represents the host-side transport objects for one worker."""

    mode: str
    host_conn: Connection | None = None
    child_endpoint: Any = None
    listener: Listener | None = None

    def finalize_after_spawn(self) -> Connection:
        """Return a connected host-side `Connection` after the worker starts."""

        if self.mode == "pipe":
            assert self.host_conn is not None
            return self.host_conn

        assert self.listener is not None
        self.host_conn = self.listener.accept()
        self.listener.close()
        self.listener = None
        return self.host_conn


def create_host_transport(mp_context) -> HostTransport:
    """Create the preferred transport, falling back when `Pipe` is unavailable."""

    try:
        host_conn, child_conn = mp_context.Pipe()
        return HostTransport(mode="pipe", host_conn=host_conn, child_endpoint=child_conn)
    except PermissionError:
        authkey = secrets.token_bytes(16)
        listener = Listener(("127.0.0.1", 0), family="AF_INET", authkey=authkey)
        return HostTransport(
            mode="socket",
            child_endpoint={
                "mode": "socket",
                "address": listener.address,
                "authkey_hex": authkey.hex(),
            },
            listener=listener,
        )


def connect_worker_transport(endpoint: Connection | dict[str, Any]) -> Connection:
    """Connect the worker to the host using the endpoint chosen by the host."""

    if hasattr(endpoint, "send") and hasattr(endpoint, "recv"):
        return endpoint

    assert isinstance(endpoint, dict)
    mode = endpoint.get("mode")
    if mode != "socket":
        raise ValueError(f"unsupported worker transport mode: {mode}")

    authkey_hex = str(endpoint["authkey_hex"])
    return Client(tuple(endpoint["address"]), family="AF_INET", authkey=bytes.fromhex(authkey_hex))
