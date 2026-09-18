from ..common import *
import gui
import qadbio
import tui



def load_q(bootcfg: BootConfig, route_msg: RouteFNCType) -> Return:
    state = UI_Stat()

    if bootcfg.UI != None:
        state.qadbio = qadbio.QaDBIO(bootcfg.screen)

    return Return(True)


def load_f(kernelState: KernelState) -> Return:
    state = kernelState.UI_Stat

    match kernelState.boot_cfg.UI:
        case"TUI":
            state.tui = tui.TextUserInterface(kernelState.boot_cfg.screen,kernelState.route_msg)
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
