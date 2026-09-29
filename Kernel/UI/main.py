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

def load_f(Bootcfg: BootConfig, state, route_msg:RouteFNCType) -> Return:

    match Bootcfg.UI:
        case"TUI":
            state.tui = TextUserInterface(Bootcfg.screen,route_msg)
            return Return(state)
        case"GUI":
            raise NotImplementedError
            #state.gui = gui.GUI(kernelState.boot_cfg.screen,route_msg)
        case _:
            return Return(state)

def loop(state: UIState) -> Return:

    if state.tui:
        state.tui.handle_event()
    return Return(state)

def shutdown(kernelState: KernelState) -> Logger:

    return Logger()
