from enum import Enum
from multiprocessing import Pipe
from multiprocessing.connection import PipeConnection

class MessageTypes(Enum):
    CONTINUE = "continue"
    SYSCALL  = "syscall"
    EXIT     = "exit"


class Message:
    def __init__(self, sender:int|str, receiver:int|str, message:dict) -> None:
        self.sender = sender
        self.receiver = receiver
        self.message = message
        pass

class Communication:
    def __init__(self, user_side:bool = False, pipe:PipeConnection|None = None)->None:
        pass

    def get_p_side(self) -> Communication:

        return Communication(True, None)

class Process:
    def __init__(self, code,pid,coms:Communication) -> None:
        pass