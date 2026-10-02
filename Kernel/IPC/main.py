from ..common import *
from .ipc import InterProcessCommunication

def load(boot_cfg: BootConfig) -> Return:
    state = IPC_State()
    state.ipc = InterProcessCommunication()
    return Return(state)

def loop(IPC_State: IPC_State) ->Return:
    IPC_State.ipc.handle_msgs()
    return Return(True)

def shutdown(IPC_State:IPC_State) -> Logger:
    return IPC_State.ipc.shutdown()