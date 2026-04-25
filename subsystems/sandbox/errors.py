"""Errors and error-code mapping for the sandbox package."""

from __future__ import annotations

PERMISSION_DENIED = -3
RESOURCE_EXHAUSTED = -5
INVALID_ARGUMENT = -6
TIMEOUT = -8
INVALID_FD = -1
IO_ERROR = -7

SANDBOX_ERROR_MAP = {
    "policy_denied": PERMISSION_DENIED,
    "invalid_args": INVALID_ARGUMENT,
    "limit_reached": RESOURCE_EXHAUSTED,
    "time_budget_exceeded": TIMEOUT,
    "invalid_fd": INVALID_FD,
    "io_error": IO_ERROR,
    "unsupported_syscall": INVALID_ARGUMENT,
}


class SandboxError(Exception):
    """Base exception for all sandbox-specific failures."""


class SandboxValidationError(SandboxError):
    """Raised when guest source code fails sandbox validation."""


class SandboxPolicyError(SandboxError):
    """Raised when a policy decision denies a requested action."""


class SandboxProtocolError(SandboxError):
    """Raised when the worker/host Pipe protocol is violated."""


class SandboxPathError(SandboxError):
    """Raised when a virtual path cannot be resolved safely."""


class SandboxHandleError(SandboxError):
    """Raised when a handle operation targets a missing or foreign handle."""


class SandboxWorkerTimeoutError(SandboxError):
    """Raised when a worker exceeds its runtime budget."""


class SandboxWorkerCrashError(SandboxError):
    """Raised when a worker terminates unexpectedly."""


def map_error_reason(reason: str) -> int:
    """Map a symbolic sandbox failure reason to an OS-style error code."""

    return SANDBOX_ERROR_MAP.get(reason, IO_ERROR)
