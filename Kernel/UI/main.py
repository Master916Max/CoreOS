from ..common import *
from .gui import GUI
from .qadbio import QaDBIO
from .tui import TextUserInterface



def load_q(bootcfg: BootConfig, route_msg: RouteFNCType) -> Return:
    state = UIState()

    if bootcfg.UI != None:
        state.qadbio = QaDBIO(bootcfg.screen)

    return Return(state)

def updateBootStateUI(UIState: UIState,bootstate: BootState) -> Return:
    if UIState.qadbio:
        UIState.qadbio.show(bootstate)
        UIState.qadbio.update()
    return Return(True)

def load_f(kernelState: KernelState) -> Return:
    state = kernelState.UI_Stat

    match kernelState.boot_cfg.UI:
        case"TUI":
            state.tui = TextUserInterface(kernelState.boot_cfg.screen,kernelState.route_msg)
            return Return(True)
        case"GUI":
            raise NotImplementedError
            #state.gui = gui.GUI(kernelState.boot_cfg.screen,route_msg)
        case _:
            return Return(True)

def loop(kernelState: KernelState) -> Return:

    return Return(True)

def shutdown(kernelState: KernelState) -> Logger:

    return Logger()
