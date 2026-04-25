"""Host-side virtual filesystem helpers for sandbox sessions."""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path, PurePosixPath

from .errors import SandboxPathError

WINDOWS_DRIVE_PATTERN = re.compile(r"^[a-zA-Z]:")
ALLOWED_FILE_MODES = {
    "r",
    "rb",
    "r+",
    "rb+",
    "r+b",
    "w",
    "wb",
    "w+",
    "wb+",
    "w+b",
    "a",
    "ab",
    "a+",
    "ab+",
    "a+b",
}


class SandboxVFS:
    """Resolves virtual paths into safe host paths under one runtime root."""

    def ensure_runtime_root(self, root: Path) -> Path:
        """Create the runtime root if needed and return its resolved path."""

        root.mkdir(parents=True, exist_ok=True)
        return root.resolve()

    def validate_open_mode(self, mode: str) -> None:
        """Reject file modes outside the explicit allowlist."""

        if mode not in ALLOWED_FILE_MODES:
            raise SandboxPathError(f"unsupported file mode: {mode}")

    def resolve_path(self, root: Path, cwd: str, virtual_path: str, *, create_parent: bool = False) -> Path:
        """Resolve a guest path under the sandbox runtime root."""

        normalized_virtual = self.normalize_virtual_path(cwd, virtual_path)
        relative_parts = PurePosixPath(normalized_virtual.lstrip("/")).parts

        runtime_root = self.ensure_runtime_root(root)
        candidate = (runtime_root.joinpath(*relative_parts)).resolve(strict=False)

        if candidate != runtime_root and runtime_root not in candidate.parents:
            raise SandboxPathError("path escapes sandbox root")

        path_to_check = candidate.parent if create_parent else candidate
        self._reject_reparse_points(runtime_root, path_to_check)

        if create_parent:
            candidate.parent.mkdir(parents=True, exist_ok=True)

        return candidate

    def normalize_virtual_path(self, cwd: str, virtual_path: str) -> str:
        """Normalize a guest path while rejecting host-specific escape syntax."""

        if not isinstance(virtual_path, str) or not virtual_path.strip():
            raise SandboxPathError("empty path is forbidden")

        raw = virtual_path.replace("\\", "/")
        if raw.startswith("//"):
            raise SandboxPathError("UNC paths are forbidden")
        if WINDOWS_DRIVE_PATTERN.match(raw) or ":" in raw:
            raise SandboxPathError("host drive paths are forbidden")

        if raw.startswith("/"):
            parts = list(PurePosixPath(raw).parts)
            base_parts: list[str] = []
        else:
            parts = list(PurePosixPath(raw).parts)
            base_parts = [part for part in PurePosixPath(cwd).parts if part not in ("", "/")]

        normalized_parts = list(base_parts)
        for part in parts:
            if part in ("", "/"):
                continue
            if part == ".":
                continue
            if part == "..":
                raise SandboxPathError("path traversal is forbidden")
            normalized_parts.append(part)

        if not normalized_parts:
            return "/"
        return "/" + "/".join(normalized_parts)

    def _reject_reparse_points(self, runtime_root: Path, candidate: Path) -> None:
        """Reject Windows reparse points between the root and the target path."""

        try:
            relative = candidate.relative_to(runtime_root)
        except ValueError as exc:
            raise SandboxPathError("path escapes sandbox root") from exc

        current = runtime_root
        for part in relative.parts:
            current = current / part
            if not current.exists():
                break

            attributes = os.lstat(current).st_file_attributes
            if attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise SandboxPathError("reparse points are forbidden inside the sandbox")


def is_binary_mode(mode: str) -> bool:
    """Return True when a file mode requests binary access."""

    return "b" in mode
