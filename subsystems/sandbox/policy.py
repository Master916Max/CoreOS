"""Policy objects and default profiles for the standalone sandbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class SyscallPolicy:
    """Describes how the host broker should authorize one syscall."""

    scope: str
    required_capability: str | None
    arg_validator: Callable[[Any], bool] | None
    resource_class: str | None = None
    audit_mode: str = "metadata"


@dataclass(frozen=True)
class SandboxProfile:
    """Immutable policy bundle used to create sandbox sessions."""

    name: str
    allowed_syscalls: frozenset[int]
    capabilities: frozenset[str]
    vfs_root: str
    cwd: str = "/"
    max_open_files: int = 16
    max_output_chars: int = 4096
    max_cpu_steps: int = 50_000
    max_runtime_ms: int = 2_000
    allowed_dlls: frozenset[str] = field(default_factory=frozenset)
    allowed_exports: frozenset[str] = field(default_factory=frozenset)
    allowed_devices: frozenset[str] = field(default_factory=frozenset)
    service_actions: frozenset[str] = field(default_factory=frozenset)


def _is_open_args(args: Any) -> bool:
    """Return True when args look like an `open(path, mode)` syscall payload."""

    return (
        isinstance(args, tuple)
        and len(args) == 2
        and isinstance(args[0], str)
        and isinstance(args[1], str)
    )


def _is_single_int_args(args: Any) -> bool:
    """Return True when args represent one integer parameter."""

    return isinstance(args, tuple) and len(args) == 1 and isinstance(args[0], int)


def _is_read_args(args: Any) -> bool:
    """Return True when args look like `read(fd, size)`."""

    return (
        isinstance(args, tuple)
        and len(args) == 2
        and isinstance(args[0], int)
        and isinstance(args[1], int)
    )


def _is_write_args(args: Any) -> bool:
    """Return True when args look like `write(fd, data)`."""

    return (
        isinstance(args, tuple)
        and len(args) == 2
        and isinstance(args[0], int)
        and isinstance(args[1], (str, bytes))
    )


def _is_seek_args(args: Any) -> bool:
    """Return True when args look like `seek(fd, offset, whence)`."""

    return (
        isinstance(args, tuple)
        and len(args) == 3
        and isinstance(args[0], int)
        and isinstance(args[1], int)
        and isinstance(args[2], int)
    )


SYSCALL_POLICIES: dict[int, SyscallPolicy] = {
    1: SyscallPolicy("both", "fs.open", _is_open_args, "file"),
    2: SyscallPolicy("both", "fs.close", _is_single_int_args, "file"),
    3: SyscallPolicy("both", "fs.read", _is_read_args, "file"),
    4: SyscallPolicy("both", "fs.write", _is_write_args, "file"),
    5: SyscallPolicy("both", "fs.seek", _is_seek_args, "file"),
    6: SyscallPolicy("both", "fs.tell", _is_single_int_args, "file"),
    129: SyscallPolicy("service", "service.register", None, "service"),
    130: SyscallPolicy("service", "service.lookup", None, "service"),
    131: SyscallPolicy("service", "service.register", None, "service"),
    132: SyscallPolicy("service", "service.unregister", None, "service"),
    301: SyscallPolicy("both", "tui.lock", None, "lease"),
    302: SyscallPolicy("both", "tui.unlock", None, "lease"),
    304: SyscallPolicy("both", "tui.print", None, "lease"),
    401: SyscallPolicy("driver", "dll.load", None, "dll"),
    403: SyscallPolicy("driver", "dll.unload", None, "dll"),
    601: SyscallPolicy("driver", "device.open", None, "device"),
}


def default_profiles(base_vfs_root: Path | None = None) -> dict[str, SandboxProfile]:
    """Return the default sandbox profiles rooted under the sandbox runtime."""

    runtime_root = base_vfs_root or (Path(__file__).resolve().parent / "runtime")

    program_caps = frozenset({"fs.open", "fs.close", "fs.read", "fs.write", "fs.seek", "fs.tell"})
    service_caps = frozenset(set(program_caps) | {"service.register", "service.lookup", "service.unregister"})
    driver_caps = frozenset(set(service_caps) | {"dll.load", "dll.unload", "device.open"})
    kernel_caps = frozenset(set(driver_caps) | {"kernel.all", "process.manage", "time.set"})

    all_known_syscalls = frozenset(SYSCALL_POLICIES.keys())

    return {
        "program": SandboxProfile(
            name="program",
            allowed_syscalls=frozenset({1, 2, 3, 4, 5, 6}),
            capabilities=program_caps,
            vfs_root=str(runtime_root / "program"),
            max_open_files=16,
            max_output_chars=4096,
            max_runtime_ms=2_000,
        ),
        "service": SandboxProfile(
            name="service",
            allowed_syscalls=frozenset({1, 2, 3, 4, 5, 6, 129, 130, 131, 132}),
            capabilities=service_caps,
            vfs_root=str(runtime_root / "service"),
            max_open_files=32,
            max_output_chars=8192,
            max_runtime_ms=5_000,
            service_actions=frozenset({"register", "lookup", "unregister"}),
        ),
        "driver": SandboxProfile(
            name="driver",
            allowed_syscalls=frozenset({1, 2, 3, 4, 5, 6, 401, 403, 601}),
            capabilities=driver_caps,
            vfs_root=str(runtime_root / "driver"),
            max_open_files=32,
            max_output_chars=8192,
            max_runtime_ms=5_000,
            allowed_dlls=frozenset({"std"}),
            allowed_devices=frozenset({"console", "disk0"}),
        ),
        "kernel": SandboxProfile(
            name="kernel",
            allowed_syscalls=all_known_syscalls,
            capabilities=kernel_caps,
            vfs_root=str(runtime_root / "kernel"),
            max_open_files=128,
            max_output_chars=32_768,
            max_runtime_ms=10_000,
            allowed_dlls=frozenset({"std"}),
            allowed_devices=frozenset({"console", "disk0"}),
            service_actions=frozenset({"register", "lookup", "unregister"}),
        ),
    }
