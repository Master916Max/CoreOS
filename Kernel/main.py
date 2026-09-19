from .UI.main import  shutdown
from .UI.main import load_q as ui_load_q
from .UI.main import load_f as ui_load_f
from .UI.main import loop as ui_loop_f
from .UI.main import shutdown as ui_shutdown
from .IPC.main import load as ipc_load
from .IPC.main import loop as ipc_loop
from .IPC.main import shutdown as ipc_shutdown
from .common import *



class Kernel:
    def __init__(self) -> None:
        self.version = "0.0.0"
        self.state = KernelState()

    def load(self,BootConf: BootConfig) -> None:
        self.bootstate = BootState()
        self.state.boot_cfg = BootConf
        ret = ipc_load(BootConf)
        if ret.error == None:
            self.state.IPC_State = ret.value
            self.state.route_msg = self.state.IPC_State.ipc.route_msg
            self.bootstate.ipc_loaded = True
        else: self.panic()

        ret = ui_load_q(BootConf, self.state.route_msg)
        if ret.error == None:
            self.state.UI_Stat = ret.value
        else: self.panic()

    def run(self) -> None:
        self.state.running = True
        while self.state.running:
            ret = ipc_loop(self.state)
            if ret.error != None:
                 self.panic()
            pass

    def shutdown(self) -> None:
        pass

    def panic(self) -> None:
        pass
        