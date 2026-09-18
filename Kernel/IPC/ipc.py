from ..common import *

class InterProcessCommunication:
    def __init__(self):
        self.msg_queue:list[Message] = []
        self.module_reg: dict[Module,list] = {Module.IPC: self.msg_queue}

        self.logger:Logger = Logger(Module.IPC)

    def route_msg(self, msg: Message):
        if not self.header_validation(msg).value:
            return self.header_validation(msg)
        if msg.to in self.module_reg:
            self.module_reg[msg.to].append(msg)
            return Return(True)
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
                            self.logger.log(0,f"Module: {module} has registered Successfully")
                            self.module_reg[module] = queue
                            self.msg_queue.remove(msg)
                            continue
                    self.route_msg(msg.answer({"action":"return","error":IPCErrorCode.InvalidMSGBody}))
                        
                    break
                case "None":
                    continue
                case _ :
                    continue
    def header_validation(self, msg:Message) -> Return:
        if msg._from == msg.to:
            return Return(False,Error(ErrorType.IPCError,IPCErrorCode.InvalidMSGHeader,"You can't send Messages to your self!"))
        elif msg.to == Module.NONE or msg._from == Module.NONE:
            return Return(False,Error(ErrorType.IPCError,IPCErrorCode.InvalidMSGHeader,"You can't send Messages with no set Sender or Receiver!"))
        return Return(True)

    def shutdown(self) -> Logger:
        return self.logger