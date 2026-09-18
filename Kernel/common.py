from .IPC.common import *
from .Core.erros import *
from .UI.common import UI_Stat
from .Core.logger import Log, Logger


class BootConfig:
    UI: str|None = None
    screen: object

class KernelState:
    boot_cfg: BootConfig
    route_msg: RouteFNCType
    UI_Stat : UI_Stat
    IPC_State: IPC_State
    error: list[Error]  = []
    running: bool       = False
    crash: bool         = False