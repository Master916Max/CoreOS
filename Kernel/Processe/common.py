from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from .process_k import ProcessManager

class ProcessState:
    manager: ProcessManager
    errors: list