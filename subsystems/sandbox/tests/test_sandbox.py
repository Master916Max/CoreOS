"""Unit and integration tests for the standalone sandbox package."""

from __future__ import annotations

import time
import unittest
from pathlib import Path

from subsystems.sandbox.manager import SandboxManager
from subsystems.sandbox.policy import SandboxProfile, default_profiles
from subsystems.sandbox.validator import SandboxValidator
from subsystems.sandbox.vfs import SandboxVFS


class SandboxValidatorTests(unittest.TestCase):
    """Tests for AST validation."""

    def test_validator_blocks_import(self) -> None:
        """Reject `import` statements before a worker is spawned."""

        ok, reason = SandboxValidator().validate("import os")
        self.assertFalse(ok)
        self.assertIn("Import", reason or "")


class SandboxPolicyTests(unittest.TestCase):
    """Tests for profile-based authorization."""

    def setUp(self) -> None:
        """Create a fresh manager for each test."""

        self.manager = SandboxManager()

    def test_program_profile_denies_driver_syscall(self) -> None:
        """A program profile must not gain access to device syscalls."""

        session = self.manager.create_session("ret = 1", "program", "policy-test")
        result = self.manager.handle_syscall_request(session.session_id, 1, 601, ())
        self.assertEqual(result, -3)


class SandboxVFSTests(unittest.TestCase):
    """Tests for virtual path resolution."""

    def test_vfs_blocks_escape(self) -> None:
        """Reject attempts to leave the runtime root with `..`."""

        vfs = SandboxVFS()
        root = Path.cwd() / "subsystems" / "sandbox" / "runtime" / "tests"
        with self.assertRaises(Exception):
            vfs.resolve_path(root, "/", "../secret.txt")


class SandboxHandleTests(unittest.TestCase):
    """Tests for host-side handle ownership."""

    def setUp(self) -> None:
        """Create a fresh manager for each test."""

        self.manager = SandboxManager()

    def test_foreign_handle_is_rejected(self) -> None:
        """One session must not use another session's handle id."""

        session_a = self.manager.create_session("ret = 1", "program", "owner-a")
        session_b = self.manager.create_session("ret = 1", "program", "owner-b")

        handle = self.manager.handle_syscall_request(session_a.session_id, 1, 1, ("/shared.txt", "w"))
        result = self.manager.handle_syscall_request(session_b.session_id, 2, 3, (handle, 10))

        self.assertEqual(result, -1)


class SandboxWorkerIntegrationTests(unittest.TestCase):
    """Integration tests for a real spawned worker process."""

    def setUp(self) -> None:
        """Create a manager and runtime root for each test."""

        self.manager = SandboxManager()

    def tearDown(self) -> None:
        """Terminate all sessions after each test."""

        for session in self.manager.list_sessions():
            if session.state not in {"cleaned"}:
                try:
                    self.manager.terminate_session(session.session_id, "test teardown")
                except Exception:
                    pass

    def test_worker_handshake_and_allowed_syscalls(self) -> None:
        """A worker should greet the host, request syscalls, and exit cleanly."""

        code = (
            'fd = syscall(1, "/hello.txt", "w")\n'
            'syscall(4, fd, "hello sandbox")\n'
            "syscall(2, fd)\n"
            'fd = syscall(1, "/hello.txt", "r")\n'
            "ret = syscall(3, fd, 64)\n"
            "syscall(2, fd)\n"
        )

        session = self.manager.create_session(code, "program", "hello-worker")
        self.manager.start_session(session.session_id)

        seen_hello = False
        seen_exit = False
        deadline = time.time() + 5
        while time.time() < deadline and not seen_exit:
            for event in self.manager.poll_events(timeout_ms=50):
                if event.type == "hello":
                    seen_hello = True
                if event.type == "syscall_request":
                    result = self.manager.handle_syscall_request(
                        event.session_id,
                        event.request_id or 0,
                        int(event.payload["syscall_id"]),
                        tuple(event.payload["args"]),
                    )
                    self.manager.send_response(event.session_id, event.request_id or 0, result)
                if event.type == "exit":
                    seen_exit = True

        self.assertTrue(seen_hello)
        self.assertTrue(seen_exit)

        file_path = session.vfs_root / "hello.txt"
        self.assertTrue(file_path.exists())
        self.assertEqual(file_path.read_text(encoding="utf-8"), "hello sandbox")

    def test_worker_timeout_generates_timeout_event(self) -> None:
        """A runaway worker should be terminated once it exceeds its budget."""

        profiles = default_profiles()
        short_program = SandboxProfile(
            name="program",
            allowed_syscalls=profiles["program"].allowed_syscalls,
            capabilities=profiles["program"].capabilities,
            vfs_root=profiles["program"].vfs_root,
            cwd=profiles["program"].cwd,
            max_open_files=profiles["program"].max_open_files,
            max_output_chars=profiles["program"].max_output_chars,
            max_cpu_steps=profiles["program"].max_cpu_steps,
            max_runtime_ms=100,
        )
        manager = SandboxManager(profiles={**profiles, "program": short_program})
        session = manager.create_session("while True:\n    pass\n", "program", "timeout-worker")
        manager.start_session(session.session_id)

        seen_timeout = False
        deadline = time.time() + 5
        while time.time() < deadline and not seen_timeout:
            for event in manager.poll_events(timeout_ms=50):
                if event.type == "timeout":
                    seen_timeout = True

        self.assertTrue(seen_timeout)
        manager.cleanup_session(session.session_id)

    def test_worker_crash_emits_crash_event(self) -> None:
        """A guest crash should be surfaced as a structured crash event."""

        session = self.manager.create_session("1 / 0\n", "program", "crash-worker")
        self.manager.start_session(session.session_id)

        seen_crash = False
        deadline = time.time() + 5
        while time.time() < deadline and not seen_crash:
            for event in self.manager.poll_events(timeout_ms=50):
                if event.type == "crash":
                    seen_crash = True
                if event.type == "syscall_request":
                    result = self.manager.handle_syscall_request(
                        event.session_id,
                        event.request_id or 0,
                        int(event.payload["syscall_id"]),
                        tuple(event.payload["args"]),
                    )
                    self.manager.send_response(event.session_id, event.request_id or 0, result)

        self.assertTrue(seen_crash)
