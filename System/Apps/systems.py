from types import FunctionType
from typing import Any


syscall : FunctionType
ret : Any


type DLLH = int

def load_libary(name) -> DLLH:
    syscall(401,name)
    return ret

def unload_libary(dllh: DLLH):
    syscall(403, dllh)
    return ret

