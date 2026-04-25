"""AST validation for sandboxed guest source code."""

from __future__ import annotations

import ast

from .errors import SandboxValidationError

FORBIDDEN_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.ClassDef,
    ast.With,
    ast.Try,
    ast.Lambda,
    ast.Global,
    ast.Nonlocal,
    ast.Raise,
    ast.Delete,
    ast.Attribute,
    ast.Await,
    ast.Yield,
    ast.AsyncFunctionDef,
)

FORBIDDEN_NAMES = {
    "__import__",
    "compile",
    "delattr",
    "dir",
    "eval",
    "exec",
    "getattr",
    "globals",
    "locals",
    "object",
    "open",
    "setattr",
    "type",
    "vars",
}


class SandboxValidator(ast.NodeVisitor):
    """Validate guest source code before it is given to a worker."""

    def validate(self, code: str) -> tuple[bool, str | None]:
        """Validate source code and return `(ok, reason)`."""

        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError as exc:
            return False, f"syntax error: {exc}"

        try:
            self.visit(tree)
        except SandboxValidationError as exc:
            return False, str(exc)
        return True, None

    def generic_visit(self, node: ast.AST) -> None:
        """Reject forbidden nodes while allowing the rest of the syntax tree."""

        if isinstance(node, FORBIDDEN_NODES):
            raise SandboxValidationError(f"forbidden node: {type(node).__name__}")
        super().generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Reject dunder names used for object graph escapes."""

        if "__" in node.id:
            raise SandboxValidationError("dunder names are forbidden")
        if node.id in FORBIDDEN_NAMES:
            raise SandboxValidationError(f"forbidden name: {node.id}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Reject decorated functions to keep execution flow explicit."""

        if node.decorator_list:
            raise SandboxValidationError("decorators are forbidden")
        self.generic_visit(node)
