import gui
import qadbio
import tui

class UI_Stat:
    gui: gui.GUI
    tui: tui.TextUserInterface
    qadbio: qadbio.QaDBIO
    errors = []
    latest_error = None