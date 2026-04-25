"""Host-side manager for the standalone V2-first sandbox package."""

from __future__ import annotations

import multiprocessing
from pathlib import Path
from time import monotonic
from typing import Any, Callable
from uuid import uuid4

from .audit import SandboxAuditTrail, redact_value
from .context import HandleEntry, ResourceLease, SandboxContext, SandboxMessage, SandboxSession
from .errors import (
    INVALID_ARGUMENT,
    INVALID_FD,
    IO_ERROR,
    PERMISSION_DENIED,
    RESOURCE_EXHAUSTED,
    TIMEOUT,
    SandboxHandleError,
    SandboxPolicyError,
    SandboxValidationError,
    map_error_reason,
)
from .policy import SYSCALL_POLICIES, SandboxProfile, default_profiles
from .transport import create_host_transport
from .validator import SandboxValidator
from .vfs import SandboxVFS, is_binary_mode
from .worker import sandbox_worker_entry

SyscallHandler = Callable[[SandboxSession, Any], Any]


class SandboxManager:
    """Host-side facade that owns worker sessions, VFS, audit, and brokering."""

    def __init__(
        self,
        profiles: dict[str, SandboxProfile] | None = None,
        *,
        base_vfs_root: Path | None = None,
    ) -> None:
        """Create a sandbox manager with spawn-based multiprocessing semantics."""

        self._mp_context = multiprocessing.get_context("spawn")
        self._profiles = profiles or default_profiles(base_vfs_root)
        self._validator = SandboxValidator()
        self._audit = SandboxAuditTrail()
        self._vfs = SandboxVFS()
        self._sessions: dict[str, SandboxSession] = {}
        self._syscall_handlers: dict[int, SyscallHandler] = {}
        self._install_builtin_handlers()

    def register_syscall_handler(self, syscall_id: int, handler: SyscallHandler) -> None:
        """Register or replace a host-side syscall handler for later integration."""

        self._syscall_handlers[syscall_id] = handler

    def create_session(self, code: str, profile_name: str = "program", process_name: str = "sandbox-process") -> SandboxSession:
        """Validate source code and create a host-owned sandbox session."""

        ok, reason = self.validate_source(code)
        if not ok:
            raise SandboxValidationError(reason or "sandbox validation failed")

        profile = self._profiles[profile_name]
        session_id = uuid4().hex
        vfs_root = self._vfs.ensure_runtime_root(Path(profile.vfs_root))
        context = SandboxContext(
            session_id=session_id,
            process_name=process_name,
            profile_name=profile.name,
            cwd=profile.cwd,
            capabilities=tuple(sorted(profile.capabilities)),
            allowed_syscalls=tuple(sorted(profile.allowed_syscalls)),
            max_runtime_ms=profile.max_runtime_ms,
            max_output_chars=profile.max_output_chars,
        )
        session = SandboxSession(
            session_id=session_id,
            process_name=process_name,
            code=code,
            profile=profile,
            context=context,
            vfs_root=vfs_root,
        )
        self._sessions[session_id] = session
        self._record_audit(
            session,
            event_type="session",
            target=process_name,
            decision="allow",
            reason="session created",
            redacted_args=None,
        )
        return session

    def start_session(self, session_id: str) -> None:
        """Spawn a worker process for a previously created sandbox session."""

        session = self._sessions[session_id]
        if session.state != "created":
            raise ValueError(f"session {session_id} is already {session.state}")

        transport = create_host_transport(self._mp_context)
        worker = self._mp_context.Process(
            target=sandbox_worker_entry,
            args=(transport.child_endpoint, session.code, session.context.to_payload()),
            name=f"sandbox-{session.process_name}",
            daemon=True,
        )

        worker.start()
        if transport.mode == "pipe" and hasattr(transport.child_endpoint, "close"):
            transport.child_endpoint.close()
        session.host_conn = transport.finalize_after_spawn()
        session.worker_process = worker
        session.state = "running"

    def validate_source(self, code: str) -> tuple[bool, str | None]:
        """Validate guest code before it is handed to a worker."""

        return self._validator.validate(code)

    def poll_events(self, timeout_ms: int = 0) -> list[SandboxMessage]:
        """Collect messages from all workers and synthesize timeout/crash events."""

        deadline = monotonic() + (max(timeout_ms, 0) / 1000.0)
        events: list[SandboxMessage] = []

        while True:
            self._collect_pipe_messages(events)
            self._collect_synthetic_events(events)

            if events or monotonic() >= deadline or timeout_ms == 0:
                return events

    def handle_syscall_request(self, session_id: str, request_id: int, syscall_id: int, args: Any) -> Any:
        """Authorize and execute one worker-requested syscall on the host."""

        session = self._sessions[session_id]
        try:
            self._authorize_syscall(session, syscall_id, args)
        except SandboxPolicyError:
            self._record_audit(
                session,
                event_type="syscall",
                target=str(syscall_id),
                decision="deny",
                reason="policy_denied",
                redacted_args=redact_value(args),
            )
            session.pending_requests.pop(request_id, None)
            return PERMISSION_DENIED
        except ValueError:
            self._record_audit(
                session,
                event_type="syscall",
                target=str(syscall_id),
                decision="deny",
                reason="invalid_args",
                redacted_args=redact_value(args),
            )
            session.pending_requests.pop(request_id, None)
            return INVALID_ARGUMENT

        handler = self._syscall_handlers.get(syscall_id)
        if handler is None:
            self._record_audit(
                session,
                event_type="syscall",
                target=str(syscall_id),
                decision="deny",
                reason="unsupported_syscall",
                redacted_args=redact_value(args),
            )
            session.pending_requests.pop(request_id, None)
            return map_error_reason("unsupported_syscall")

        try:
            result = handler(session, args)
        except SandboxHandleError:
            result = INVALID_FD
        except OSError:
            result = IO_ERROR

        self._record_audit(
            session,
            event_type="syscall",
            target=str(syscall_id),
            decision="allow",
            reason="handler_executed",
            redacted_args=redact_value(args),
        )
        session.pending_requests.pop(request_id, None)
        return result

    def send_response(self, session_id: str, request_id: int, result: Any) -> None:
        """Send one syscall response back to the worker."""

        session = self._sessions[session_id]
        if session.host_conn is None:
            raise RuntimeError(f"session {session_id} has no live Pipe")

        message = SandboxMessage(
            type="syscall_response",
            session_id=session_id,
            request_id=request_id,
            payload={"result": result},
        )
        session.host_conn.send(message.to_dict())

    def terminate_session(self, session_id: str, reason: str) -> None:
        """Stop a worker, release its host resources, and mark it terminated."""

        session = self._sessions[session_id]
        if session.host_conn is not None:
            try:
                session.host_conn.send(
                    SandboxMessage(
                        type="terminate",
                        session_id=session_id,
                        payload={"reason": reason},
                    ).to_dict()
                )
            except (BrokenPipeError, EOFError, OSError):
                pass

        if session.worker_process is not None and session.worker_process.is_alive():
            session.worker_process.terminate()
            session.worker_process.join(timeout=1)

        session.state = "terminated"
        session.last_error = reason
        self.cleanup_session(session_id)

    def cleanup_session(self, session_id: str) -> None:
        """Close handles, release leases, and close transport objects for one session."""

        session = self._sessions[session_id]

        # Lease cleanup is intentionally simple here because the sandbox package
        # does not own the real OS resources yet. Later integration will map
        # cleanup_action strings to actual TUI/service/device release hooks.
        session.leases.clear()

        for entry in list(session.handles.values()):
            try:
                entry.file_obj.close()
            except OSError:
                pass
        session.handles.clear()

        if session.host_conn is not None:
            try:
                session.host_conn.close()
            except OSError:
                pass
            session.host_conn = None

        if session.worker_process is not None and session.worker_process.is_alive():
            session.worker_process.join(timeout=1)

        session.state = "cleaned"

    def get_session(self, session_id: str) -> SandboxSession:
        """Return one sandbox session by id."""

        return self._sessions[session_id]

    def list_sessions(self) -> list[SandboxSession]:
        """Return all known sandbox sessions."""

        return list(self._sessions.values())

    def _collect_pipe_messages(self, events: list[SandboxMessage]) -> None:
        """Read all currently available messages from all running workers."""

        for session in self._sessions.values():
            if session.host_conn is None:
                continue

            while session.host_conn.poll():
                try:
                    raw_message = session.host_conn.recv()
                except EOFError:
                    try:
                        session.host_conn.close()
                    except OSError:
                        pass
                    session.host_conn = None
                    break

                message = SandboxMessage.from_dict(raw_message)

                if message.type == "heartbeat":
                    session.limits.last_heartbeat_at = monotonic()
                elif message.type in {"stdout", "stderr"}:
                    text = str(message.payload.get("text", ""))
                    session.limits.output_chars += len(text)
                    if session.limits.output_chars > session.profile.max_output_chars:
                        session.last_error = "output budget exceeded"
                        events.append(
                            SandboxMessage(
                                type="policy_error",
                                session_id=session.session_id,
                                payload={"reason": "output budget exceeded"},
                            )
                        )
                        self.terminate_session(session.session_id, "output budget exceeded")
                        break
                elif message.type == "syscall_request" and message.request_id is not None:
                    session.pending_requests[message.request_id] = message
                elif message.type == "exit":
                    session.exit_code = int(message.payload.get("exit_code", 0))
                    session.state = "exited"
                elif message.type in {"crash", "policy_error"}:
                    session.last_error = str(message.payload.get("reason") or message.payload.get("error"))

                events.append(message)

    def _collect_synthetic_events(self, events: list[SandboxMessage]) -> None:
        """Generate timeout or crash events that the worker cannot send itself."""

        for session in self._sessions.values():
            if session.state not in {"running", "exited"}:
                continue

            elapsed_ms = (monotonic() - session.limits.started_at) * 1000.0
            if session.state == "running" and elapsed_ms > session.profile.max_runtime_ms:
                events.append(
                    SandboxMessage(
                        type="timeout",
                        session_id=session.session_id,
                        payload={"reason": "runtime budget exceeded"},
                    )
                )
                self._record_audit(
                    session,
                    event_type="runtime",
                    target=session.process_name,
                    decision="deny",
                    reason="time_budget_exceeded",
                    redacted_args=None,
                )
                self.terminate_session(session.session_id, "runtime budget exceeded")
                continue

            process = session.worker_process
            if session.state == "running" and process is not None and not process.is_alive():
                events.append(
                    SandboxMessage(
                        type="crash",
                        session_id=session.session_id,
                        payload={"error": "worker exited unexpectedly"},
                    )
                )
                self._record_audit(
                    session,
                    event_type="runtime",
                    target=session.process_name,
                    decision="deny",
                    reason="worker_crash",
                    redacted_args=None,
                )
                self.cleanup_session(session.session_id)

    def _authorize_syscall(self, session: SandboxSession, syscall_id: int, args: Any) -> None:
        """Authorize one syscall against the profile allowlist and capability map."""

        if syscall_id not in session.profile.allowed_syscalls:
            raise SandboxPolicyError(f"syscall {syscall_id} is not allowed for {session.profile.name}")

        policy = SYSCALL_POLICIES.get(syscall_id)
        if policy is None:
            raise SandboxPolicyError(f"syscall {syscall_id} has no declared policy")
        if policy.required_capability and policy.required_capability not in session.profile.capabilities:
            raise SandboxPolicyError(f"missing capability {policy.required_capability}")
        if policy.arg_validator and not policy.arg_validator(args):
            raise ValueError(f"invalid arguments for syscall {syscall_id}")

    def _install_builtin_handlers(self) -> None:
        """Register the standalone file syscall handlers shipped with the sandbox."""

        self._syscall_handlers.update(
            {
                1: self._handle_open,
                2: self._handle_close,
                3: self._handle_read,
                4: self._handle_write,
                5: self._handle_seek,
                6: self._handle_tell,
            }
        )

    def _handle_open(self, session: SandboxSession, args: Any) -> int:
        """Host-side implementation of `open(path, mode)` for sandbox workers."""

        virtual_path, mode = args
        self._vfs.validate_open_mode(mode)
        create_parent = any(flag in mode for flag in ("w", "a", "+"))
        host_path = self._vfs.resolve_path(session.vfs_root, session.context.cwd, virtual_path, create_parent=create_parent)

        if len(session.handles) >= session.profile.max_open_files:
            return RESOURCE_EXHAUSTED

        open_kwargs: dict[str, Any] = {"mode": mode}
        if not is_binary_mode(mode):
            open_kwargs["encoding"] = "utf-8"

        file_obj = open(host_path, **open_kwargs)
        handle_id = session.next_handle_id
        session.next_handle_id += 1
        session.handles[handle_id] = HandleEntry(
            handle_id=handle_id,
            owner_session_id=session.session_id,
            virtual_path=virtual_path,
            host_path=str(host_path),
            mode=mode,
            file_obj=file_obj,
        )
        return handle_id

    def _handle_close(self, session: SandboxSession, args: Any) -> int:
        """Host-side implementation of `close(fd)` for sandbox workers."""

        handle_entry = self._require_handle(session, args[0])
        handle_entry.file_obj.close()
        session.handles.pop(handle_entry.handle_id, None)
        return 0

    def _handle_read(self, session: SandboxSession, args: Any) -> Any:
        """Host-side implementation of `read(fd, size)` for sandbox workers."""

        handle_entry = self._require_handle(session, args[0])
        if "r" not in handle_entry.mode and "+" not in handle_entry.mode:
            return PERMISSION_DENIED
        return handle_entry.file_obj.read(args[1])

    def _handle_write(self, session: SandboxSession, args: Any) -> int:
        """Host-side implementation of `write(fd, data)` for sandbox workers."""

        handle_entry = self._require_handle(session, args[0])
        if not any(flag in handle_entry.mode for flag in ("w", "a", "+")):
            return PERMISSION_DENIED
        data = args[1]
        written = handle_entry.file_obj.write(data)
        handle_entry.file_obj.flush()
        return written if isinstance(written, int) else len(data)

    def _handle_seek(self, session: SandboxSession, args: Any) -> int:
        """Host-side implementation of `seek(fd, offset, whence)` for sandbox workers."""

        handle_entry = self._require_handle(session, args[0])
        handle_entry.file_obj.seek(args[1], args[2])
        return 0

    def _handle_tell(self, session: SandboxSession, args: Any) -> int:
        """Host-side implementation of `tell(fd)` for sandbox workers."""

        handle_entry = self._require_handle(session, args[0])
        return int(handle_entry.file_obj.tell())

    def _require_handle(self, session: SandboxSession, handle_id: int) -> HandleEntry:
        """Return a valid handle entry or raise when it does not belong to the session."""

        handle_entry = session.handles.get(handle_id)
        if handle_entry is None or handle_entry.owner_session_id != session.session_id:
            raise SandboxHandleError(f"invalid or foreign handle: {handle_id}")
        return handle_entry

    def _record_audit(
        self,
        session: SandboxSession,
        *,
        event_type: str,
        target: str,
        decision: str,
        reason: str,
        redacted_args: Any,
    ) -> None:
        """Record one audit event globally and on the session object."""

        record = self._audit.record(
            pid=session.session_id,
            event_type=event_type,
            target=target,
            decision=decision,
            reason=reason,
            redacted_args=redacted_args,
        )
        session.audit_records.append(record)
