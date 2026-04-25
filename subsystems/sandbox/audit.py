"""Audit helpers for sandbox decisions and message redaction."""

from __future__ import annotations

from typing import Any

from .context import SandboxAuditRecord


def redact_value(value: Any) -> Any:
    """Return a redacted version of a value safe for audit logs."""

    if isinstance(value, dict):
        return {str(key): "<redacted>" for key in value}
    if isinstance(value, (list, tuple, set)):
        return ["<redacted>" for _ in value]
    if isinstance(value, (str, bytes)):
        return "<redacted>"
    if value is None:
        return None
    return "<redacted>"


class SandboxAuditTrail:
    """Collects audit records emitted by the host-side sandbox manager."""

    def __init__(self) -> None:
        """Initialize an empty audit trail."""

        self.records: list[SandboxAuditRecord] = []

    def record(
        self,
        *,
        pid: str,
        event_type: str,
        target: str,
        decision: str,
        reason: str,
        redacted_args: Any,
    ) -> SandboxAuditRecord:
        """Create and store one audit record."""

        record = SandboxAuditRecord(
            pid=pid,
            event_type=event_type,
            target=target,
            decision=decision,
            reason=reason,
            redacted_args=redacted_args,
        )
        self.records.append(record)
        return record
