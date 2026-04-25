"""Dataclasses used by the standalone sandbox package."""

from __future__ import annotations

from dataclasses import dataclass, field
from multiprocessing.connection import Connection
from multiprocessing.process import BaseProcess
from pathlib import Path
from time import monotonic, time
from typing import Any, IO

from .policy import SandboxProfile


@dataclass
class LimitState:
    """Tracks mutable runtime counters for one sandbox session."""

    started_at: float = field(default_factory=monotonic)
    last_heartbeat_at: float = field(default_factory=monotonic)
    cpu_steps: int = 0
    output_chars: int = 0


@dataclass
class HandleEntry:
    """Represents one host-owned file handle belonging to a sandbox session."""

    handle_id: int
    owner_session_id: str
    virtual_path: str
    host_path: str
    mode: str
    file_obj: IO[Any] = field(repr=False, compare=False)


@dataclass
class ResourceLease:
    """Represents one exclusive host-side resource reservation."""

    resource_id: str
    owner_session_id: str
    expires_at: float | None
    cleanup_action: str


@dataclass
class SandboxAuditRecord:
    """Represents one audit event emitted by the sandbox host broker."""

    pid: str
    event_type: str
    target: str
    decision: str
    reason: str
    redacted_args: Any
    timestamp: float = field(default_factory=time)


@dataclass(frozen=True)
class SandboxContext:
    """Serializable worker-visible metadata for one sandboxed process."""

    session_id: str
    process_name: str
    profile_name: str
    cwd: str
    capabilities: tuple[str, ...]
    allowed_syscalls: tuple[int, ...]
    max_runtime_ms: int
    max_output_chars: int

    def to_payload(self) -> dict[str, Any]:
        """Return a JSON-like payload that can be sent to the worker."""

        return {
            "session_id": self.session_id,
            "process_name": self.process_name,
            "profile_name": self.profile_name,
            "cwd": self.cwd,
            "capabilities": list(self.capabilities),
            "allowed_syscalls": list(self.allowed_syscalls),
            "max_runtime_ms": self.max_runtime_ms,
            "max_output_chars": self.max_output_chars,
        }


@dataclass(frozen=True)
class SandboxMessage:
    """Represents one structured Pipe message exchanged with a worker."""

    type: str
    session_id: str
    request_id: int | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict safe to send over the Pipe transport."""

        return {
            "type": self.type,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, raw_message: dict[str, Any]) -> "SandboxMessage":
        """Build a message object from a received plain dict."""

        return cls(
            type=str(raw_message["type"]),
            session_id=str(raw_message["session_id"]),
            request_id=raw_message.get("request_id"),
            payload=dict(raw_message.get("payload", {})),
            timestamp=float(raw_message.get("timestamp", time())),
        )


@dataclass
class SandboxSession:
    """Stores all host-side runtime state for one sandbox worker."""

    session_id: str
    process_name: str
    code: str
    profile: SandboxProfile
    context: SandboxContext
    vfs_root: Path
    state: str = "created"
    limits: LimitState = field(default_factory=LimitState)
    handles: dict[int, HandleEntry] = field(default_factory=dict)
    leases: dict[str, ResourceLease] = field(default_factory=dict)
    audit_records: list[SandboxAuditRecord] = field(default_factory=list)
    pending_requests: dict[int, SandboxMessage] = field(default_factory=dict)
    next_handle_id: int = 3
    exit_code: int | None = None
    last_error: str | None = None
    host_conn: Connection | None = field(default=None, repr=False, compare=False)
    worker_process: BaseProcess | None = field(default=None, repr=False, compare=False)

