from typing import  TYPE_CHECKING

if TYPE_CHECKING:from .gui import GUI
if TYPE_CHECKING:from .qadbio import QaDBIO
if TYPE_CHECKING:from .tui import TextUserInterface

class UI_Stat:
    gui: GUI
    tui: TextUserInterface
    qadbio: QaDBIO
    errors = []
    latest_error = None

class BootState:
    ipc_loaded: bool = False
    ui_loaded: bool = False
    process_loaded: bool = False
    core_loaded: bool = False