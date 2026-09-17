from .common import Message,Module

from ..Core.erros import Return, ErrorType, IPCErrorCode, Error

class InterProcessCommunication:
    def __init__(self):
        self.msg_queue = []

        self.module_reg: dict[Module,list] = {Module.IPC: self.msg_queue}


    def route_msg(self, msg: Message):
        if msg.to in self.module_reg:
            self.module_reg[msg.to].append(msg)
        else:
            return Return(False,Error(ErrorType.IPCError,IPCErrorCode.ModuleNotRegistered,"The Requested Module has not been Registered at the Moment"))
