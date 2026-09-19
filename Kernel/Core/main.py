from ..common import *

def load(boot_cfg: BootConfig, route_msg:RouteFNCType) -> Return:
    core_state = CoreState()

    core_state.mem_mgr = MemoryManager(route_msg)
    core_state.perm_mgr = PermissionManager(route_msg)
    if boot_cfg.debugger_enabled:
        core_state.debugger = Debugger(route_msg)

    return Return(core_state)

def loop(core_state:CoreState) -> Return:

    pass