from ..common import *
from .ipc import InterProcessCommunication

def load(boot_cfg: BootConfig) -> Return:
    state = IPC_State()
    state.ipc = InterProcessCommunication()
    return Return(state)

def loop(kernelState: KernelState) ->Return:
    kernelState.IPC_State.ipc.handle_msgs()
    return Return(True)

def shutdown(kernelState:KernelState) -> Logger:
    return kernelState.IPC_State.ipc.shutdown()