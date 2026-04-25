"""Worker runtime for the V2-first standalone sandbox."""

from __future__ import annotations

import traceback
from multiprocessing.connection import Connection
from typing import Any

from .context import SandboxContext, SandboxMessage
from .errors import SandboxProtocolError
from .namespace import build_worker_namespace
from .transport import connect_worker_transport
from .validator import SandboxValidator


class WorkerBrokerProxy:
    """Proxy object used by the worker to talk to the host broker."""

    def __init__(self, conn: Connection, session_id: str) -> None:
        """Bind the proxy to one Pipe endpoint and one session id."""

        self._conn = conn
        self._session_id = session_id
        self._next_request_id = 1

    def emit_hello(self, payload: dict[str, Any]) -> None:
        """Send the initial hello message to the host."""

        self._send("hello", payload)

    def emit_heartbeat(self) -> None:
        """Send a heartbeat so the host can observe forward progress."""

        self._send("heartbeat", {})

    def emit_stdout(self, text: str) -> None:
        """Send worker stdout text to the host."""

        self._send("stdout", {"text": text})

    def emit_stderr(self, text: str) -> None:
        """Send worker stderr text to the host."""

        self._send("stderr", {"text": text})

    def emit_exit(self, exit_code: int = 0) -> None:
        """Notify the host that the worker finished normally."""

        self._send("exit", {"exit_code": exit_code})

    def emit_crash(self, error: str, traceback_text: str) -> None:
        """Notify the host that guest execution crashed."""

        self._send("crash", {"error": error, "traceback": traceback_text})

    def request_syscall(self, syscall_id: int, *args: Any) -> Any:
        """Send a syscall request and wait for one matching response."""

        request_id = self._next_request_id
        self._next_request_id += 1

        payload = {"syscall_id": syscall_id, "args": args}
        self._send("syscall_request", payload, request_id=request_id)

        while True:
            raw_message = self._conn.recv()
            message = SandboxMessage.from_dict(raw_message)

            if message.type == "syscall_response" and message.request_id == request_id:
                return message.payload.get("result")
            if message.type == "terminate":
                raise SystemExit(message.payload.get("reason", "terminated by host"))

            raise SandboxProtocolError(f"unexpected worker message while waiting: {message.type}")

    def _send(self, message_type: str, payload: dict[str, Any], request_id: int | None = None) -> None:
        """Send one structured dict message across the Pipe."""

        message = SandboxMessage(
            type=message_type,
            session_id=self._session_id,
            request_id=request_id,
            payload=payload,
        )
        self._conn.send(message.to_dict())


class SandboxWorkerMain:
    """Boots the restricted worker runtime and executes guest code."""

    def __init__(self, conn: Connection, code: str, context_payload: dict[str, Any]) -> None:
        """Create a worker runtime bound to one Pipe and one source blob."""

        self._conn = conn
        self._code = code
        self._context = SandboxContext(
            session_id=str(context_payload["session_id"]),
            process_name=str(context_payload["process_name"]),
            profile_name=str(context_payload["profile_name"]),
            cwd=str(context_payload["cwd"]),
            capabilities=tuple(context_payload["capabilities"]),
            allowed_syscalls=tuple(context_payload["allowed_syscalls"]),
            max_runtime_ms=int(context_payload["max_runtime_ms"]),
            max_output_chars=int(context_payload["max_output_chars"]),
        )
        self._proxy = WorkerBrokerProxy(conn, self._context.session_id)

    def run(self) -> None:
        """Run guest code inside the worker and report structured events."""

        self._proxy.emit_hello(
            {
                "process_name": self._context.process_name,
                "profile_name": self._context.profile_name,
            }
        )
        self._proxy.emit_heartbeat()

        ok, reason = SandboxValidator().validate(self._code)
        if not ok:
            self._proxy._send("policy_error", {"reason": reason})
            self._proxy.emit_exit(1)
            return

        namespace = build_worker_namespace(self._proxy.request_syscall, self._proxy.emit_stdout)
        try:
            compiled = compile(self._code, f"<sandbox:{self._context.session_id}>", "exec")
            exec(compiled, namespace, namespace)
            self._proxy.emit_exit(0)
        except SystemExit as exc:
            exit_code = int(exc.code) if isinstance(exc.code, int) else 1
            self._proxy.emit_exit(exit_code)
        except Exception as exc:  # noqa: BLE001 - worker must capture guest crashes.
            trace = traceback.format_exc()
            self._proxy.emit_crash(str(exc), trace)
            self._proxy.emit_exit(1)


def sandbox_worker_entry(endpoint: Connection | dict[str, Any], code: str, context_payload: dict[str, Any]) -> None:
    """Top-level process entrypoint required by Windows `spawn` mode."""

    conn = connect_worker_transport(endpoint)
    try:
        worker = SandboxWorkerMain(conn, code, context_payload)
        worker.run()
    finally:
        conn.close()
