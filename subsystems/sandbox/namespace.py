"""Restricted namespace construction for sandbox workers."""

from __future__ import annotations

from typing import Any, Callable


def _safe_print_factory(emit_stdout: Callable[[str], None]) -> Callable[..., None]:
    """Build a safe `print` replacement that routes through the host broker."""

    def safe_print(*values: Any, sep: str = " ", end: str = "\n") -> None:
        text = sep.join(str(value) for value in values) + end
        emit_stdout(text)

    return safe_print


SAFE_BUILTINS = {
    "abs": abs,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "range": range,
    "str": str,
    "sum": sum,
    "tuple": tuple,
}


def build_worker_namespace(
    syscall_callable: Callable[..., Any],
    emit_stdout: Callable[[str], None],
) -> dict[str, object]:
    """Create the restricted global namespace used inside the worker."""

    builtins = dict(SAFE_BUILTINS)
    builtins["print"] = _safe_print_factory(emit_stdout)

    return {
        "__builtins__": builtins,
        "__name__": "__sandbox__",
        "ret": None,
        "syscall": syscall_callable,
    }
