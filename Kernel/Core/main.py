from ..common import *

from .memory import MemoryManager
from .permissions import PermissionManager
from .debug import Debugger

def load(boot_cfg: BootConfig, route_msg:RouteFNCType) -> Return:
    core_state = CoreState()

    core_state.mem_mgr = MemoryManager(route_msg)
    core_state.perm_mgr = PermissionManager(route_msg)
    if boot_cfg.debugger_enabled:
        core_state.debugger = Debugger(route_msg)
        core_state.debugger.start()

    return Return(core_state)

def loop(core_state:CoreState) -> Return:

    core_state.mem_mgr.handle_msgs()
    #! core_state.perm_mgr
    return Return(core_state)

def shutdown(core_state: CoreState) -> Logger:
    logger = Logger(Module.NONE)

    logger += core_state.mem_mgr.shutdown()
    if core_state.debugger:
        logger += core_state.debugger.shutdown()

    return logger