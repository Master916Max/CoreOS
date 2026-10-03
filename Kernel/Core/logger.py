from io import UnsupportedOperation

from uuid import uuid4

from ..IPC.common import Module

class Log:
    def __init__(self,level:int,module:Module,message:str) -> None:
        if not isinstance(level,int) or not isinstance(module,Module) or not isinstance(message,str):
            raise TypeError("Invalid argument types")
        self.level = level
        self.module = module.value
        self.message = message
        self.id = uuid4()

    def __str__(self):
        return f"[{self.level}] {self.module}: {self.message}"

class Logger:
    def __init__(self,module:Module = Module.KERNEL) -> None:
        if not isinstance(module,Module):
            raise TypeError("Invalid argument types")
        self.module = module
        self.logs = []

    def log(self,level:int,message:str) -> None:
        self.logs.append(Log(level,self.module,message))

    def get_logs(self,level:int=0) -> list[Log]:
        if not isinstance(level,int):
            raise TypeError("Invalid argument types")
        return [log for log in self.logs if log.level >= level]

    def get_logs_s(self,level:int=0) -> str:
        if not isinstance(level,int):
            raise TypeError("Invalid argument types")
        return "\n".join([str(log) for log in self.logs if log.level >= level])

    def __add__(self, other: Logger):
        if isinstance(other,Logger):
            for log in other.logs:
                self.logs.append(log)
            return self
        else:
            raise UnsupportedOperation()
