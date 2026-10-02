from __future__ import annotations
from typing import TYPE_CHECKING
from .erros import *
from .logger import *


if TYPE_CHECKING:from .debug import Debugger
if TYPE_CHECKING:from .memory import MemoryManager
if TYPE_CHECKING:from .permissions import PermissionManager

class CoreState:
    debugger: Debugger|None = None
    mem_mgr: MemoryManager|None = None
    perm_mgr: PermissionManager|None = None