from .UI.main import load_q,load_f, loop, shutdown
from .common import *



class Kernel:
    def __init__(self):
        self.version = "0.2.0"

    def load(self,BootConf: BootConfig):
        pass

    def run(self):
        pass

    def shutdown(self):
        pass

    def panic(self):
        pass
        