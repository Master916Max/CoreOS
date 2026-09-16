from enum import Enum
from typing import Any

class ErrorType(Enum):
    LoggerError = 0,
    MemoryError = 1,
    PermissionError = 2,
    IPCError = 3,

class ErrorCode(Enum):
    pass

class LoggerErrorCode(ErrorCode):
    InvalidArgumentTypes = 0,
    InvalidLogLevel = 1,

class MemoryErrorCode(ErrorCode):
    OutOfMemory = 0,
    MemoryCorruptionDetected = 1,
    NoPermissionToAccessMemory = 2,

class PermissionErrorCode(ErrorCode):
    InvalidPermission = 0,
    NotEnoughPermission = 1,
    NotAllowedToRead = 2,
    NotAllowedToWrite = 3,
    NotAllowedToExecute = 4

class IPCErrorCode(ErrorCode):
    ModuleNotRegistered = 0,
    InvalideMSGBody = 1,
    InvalideMSGHeader = 2

class Error:
    def __init__(self,error_type:ErrorType,error_code:ErrorCode,message:str) -> None:
        if not isinstance(error_type,ErrorType) or not isinstance(error_code,int) or not isinstance(message,str):
            raise TypeError("Invalid argument types")
        self.error_type = error_type
        self.error_code = error_code
        self.message = message

    def __str__(self):
        return f"[{self.error_type.name}] {self.error_code}: {self.message}"

class Return:
    def __init__(self,value:Any,error:Error|None=None) -> None:
        if error is not None and not isinstance(error,Error):
            raise TypeError("Invalid argument types")
        self.value = value
        self.error = error

    def handle(self):
        if self.error is not None:
            return self.error
        else:
            return self.value