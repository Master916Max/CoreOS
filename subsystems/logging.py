
import time 
from datetime import datetime


class Log:
    def __init__(self,priority:int = 0, message:str = ""):
        self.priority = priority
        self.message = message
        self.time = time.time()
    
    def __str__(self) -> str:
        return f"{datetime.fromtimestamp(self.time).strftime("%d.%m.%Y|%H:%M:%S:%f")}-[{self.priority}] {self.message}"

class Logger:
    def __init__(self) -> None:
        self.logs: dict[float, Log] = {}
    
    def log(self, priority: int, message: str):
        log_entry = Log(priority, message)
        self.logs[log_entry.time] = log_entry
    
    def __add__(self, other: Logger):
        self.logs.update(other.logs)
        return self

    def get_logs(self)-> dict[float,Log]:
        return self.logs