import sys
import time

# System Wide Defs
from .common import *

# Core Functions
from .Core.main import load as core_load
from .Core.main import loop as core_loop
from .Core.main import shutdown as core_shutdown

# IPC Funtions
from .IPC.main import load as ipc_load
from .IPC.main import loop as ipc_loop
from .IPC.main import shutdown as ipc_shutdown
from .UI.main import load_f as ui_load_f
from .UI.main import load_q as ui_load_q
from .UI.main import loop as ui_loop_f

# UI Functions
from .UI.main import shutdown, updateBootStateUI
from .UI.main import shutdown as ui_shutdown


class Kernel:
    def __init__(self) -> None:
        self.version = "0.0.1"
        self.msg_queue: list[Message] = []
        self.state = KernelState()
        self.state.logger = Logger(Module.KERNEL)

    def load(self,BootConf: BootConfig) -> None:
        self.bootstate = BootState()
        self.state.boot_cfg = BootConf
        
        ret = ipc_load(BootConf)
        if ret.error == None:
            self.state.IPC_State = ret.value
            self.state.route_msg = self.state.IPC_State.ipc.route_msg
            self.bootstate.ipc_loaded = True
        else: self.panic()
        time.sleep(0.01)

        ret = ui_load_q(BootConf, self.state.route_msg)
        if ret.error == None:
            self.state.UI_Stat = ret.value
        else: self.panic()
        updateBootStateUI(self.state.UI_Stat,self.bootstate)
        time.sleep(0.01)

        ret = core_load(BootConf, self.state.route_msg)
        if ret.error == None:
            self.state.Core_State = ret.value
            self.bootstate.core_loaded = True
        else: self.panic()
        updateBootStateUI(self.state.UI_Stat,self.bootstate)
        time.sleep(0.01)

        ret = ui_load_f(BootConf, self.state.UI_Stat, self.state.route_msg)
        if ret.error == None:
            self.state.UI_Stat = ret.value
            self.bootstate.ui_loaded = True
        else:
            self.panic()
        updateBootStateUI(self.state.UI_Stat,self.bootstate)
        time.sleep(0.01)

        self.register_ipc()



    def run(self) -> None:
        self.state.running = True
        while self.state.running:
            ret = ipc_loop(self.state.IPC_State)
            if ret.error != None:
                 self.panic()
            ret = ui_loop_f(self.state.UI_Stat)
            if ret.error != None:
                self.panic()
            ret = core_loop(self.state.Core_State)
            if ret.error != None:
                self.panic()
            self.handle_msg()
        self.shutdown()

            
    def register_ipc(self) -> None:
        reg_msg = Message()
        reg_msg.set_header(Module.KERNEL,Module.IPC,False)
        reg_msg.set_body({
            "action": "register",
            "module": Module.KERNEL,
            "queue": self.msg_queue
        })
        self.state.route_msg(reg_msg)

    def handle_msg(self) -> None:
        for msg in self.msg_queue:
            body = msg.get_body()
            action = body.get("action", None)
            sender = msg.get_header().get("from")
            if action:
                match action:
                    case "shutdown":
                        self.state.running = False
                    case _:
                        msg.answer({
                            "action" : "return",
                            "error" : "Unsupported Action"
                        })


    def shutdown(self) -> None:
        self.state.logger = self.state.logger.__add__(core_shutdown(self.state.Core_State))
        self.state.logger = self.state.logger.__add__(ui_shutdown(self.state.UI_Stat))
        self.state.logger = self.state.logger.__add__(ipc_shutdown(self.state.IPC_State))

        print(self.state.logger.get_logs_s(-5))
        self.panic()
            
            

    def panic(self) -> None:
        sys.exit(120000)
        pass
        