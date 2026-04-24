
from enum import Enum

class SyscallReturnType(Enum):
    Succes = 0,
    Wait = 1,
    Error = 2

class SyscallReturn:
    def __init__(self, typee: SyscallReturnType, value):
        self.type = typee
        self.value = value
    
class ErrorCode(Enum):
    pass