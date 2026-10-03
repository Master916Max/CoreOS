from ..common import *
from .process_k import ProcessManager


def load(boot_cfg: BootConfig, route_msg: RouteFNCType) -> Return:
    state = ProcessState()
    state.manager = ProcessManager(route_msg)
    state.errors = []
    return Return(state)

def loop(state: ProcessState) -> Return:
    state.manager.loop()
    return Return(state)

def shutdown(state: ProcessState) -> Logger:
    return state.manager.shutdown()