from .common import Message,Module

from ..Core.erros import Return, ErrorType, IPCErrorCode, Error

class InterProcessCommunication:
    def __init__(self):
        self.msg_queue:list[Message] = []

        self.module_reg: dict[Module,list] = {Module.IPC: self.msg_queue}


    def route_msg(self, msg: Message):
        if not self.header_validation(msg).value:
            return self.header_validation(msg)
        if msg.to in self.module_reg:
            self.module_reg[msg.to].append(msg)
        else:
            return Return(False,Error(ErrorType.IPCError,IPCErrorCode.ModuleNotRegistered,"The Requested Module has not been Registered at the Moment"))

    def handle_msgs(self) ->None:
        for msg in self.msg_queue:
            match msg.get_body().get("action","None"):
                case "register":
                    module = msg.get_body().get("module", None)
                    if module and not module in self.module_reg:
                        queue = msg.get_body().get("queue", None)
                        if queue:
                            self.module_reg[module] = queue
                            self.msg_queue.remove(msg)
                            continue
                    msg.answer
                        
                    break
                case "None":
                    continue
                case _ :
                    continue
    def header_validation(self, msg:Message) -> Return:
        if msg._from == msg.to:
            return Return(False,Error(ErrorType.IPCError,IPCErrorCode.InvalideMSGHeader,"You can´t send Messages to your self!"))
        elif msg.to == Module.NONE or msg._from == Module.NONE:
            return Return(False,Error(ErrorType.IPCError,IPCErrorCode.InvalideMSGHeader,"You can´t send Messages with no set Sender or Reciever!"))
        return Return(True)
        