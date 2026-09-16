
class Log:
    def __init__(self,level:int,module:str,message:str) -> None:
        if not isinstance(level,int) or not isinstance(module,str) or not isinstance(message,str):
            raise TypeError("Invalid argument types")
        self.level = level
        self.module = module
        self.message = message

    def __str__(self):
        return f"[{self.level}] {self.module}: {self.message}"

class Logger:
    def __init__(self,module:str="Kernel") -> None:
        if not isinstance(module,str):
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
