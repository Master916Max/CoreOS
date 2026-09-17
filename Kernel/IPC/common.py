from uuid import UUID
from enum import Enum

class Module(Enum):
    KERNEL = "kernel"
    MEMORY = "memory"
    IPC = "ipc"
    NONE = ""



class Message:
    def __init__(self):
        self._from = Module.NONE
        self.to = Module.NONE
        self.content = {}
        self.answer_required = False
        self.msg_id = UUID()

    def set_header(self,_from:Module,to:Module,answer_required:bool=False):
        self._from = _from
        self.to = to
        self.answer_required = answer_required

    def set_body(self,content:dict):
        self.content = content

    def get_header(self):
        return {
            "_from": self._from,
            "to": self.to,
            "answer_required": self.answer_required
        }
    def get_body(self):
        return self.content

    def answer(self,content:dict):
        _msg = Message()
        _msg.set_header(self.to,self._from,False)
        _msg.set_body(content)
        _msg.msg_id = self.msg_id
        return _msg
