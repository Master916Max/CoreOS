from .IPC.common import *
from .Core.common import *
from .UI.common import UIState, BootState


class BootConfig:
    UI: str|None = None
    screen: object
    debugger_enabled: bool = False

class KernelState:
    boot_cfg: BootConfig
    route_msg: RouteFNCType
    UI_Stat : UIState
    IPC_State: IPC_State
    error: list[Error]  = []
    running: bool       = False
    crash: bool         = False