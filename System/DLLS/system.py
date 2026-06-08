from types import FunctionType
syscall : FunctionType

class System:
    def __init__(self):
        pass

    def load(self):
        self.mem_pos = syscall()

    def unload(self):
        pass

    def load_library(self, name):
        pass

    def require_tui(self):
        syscall(301)

    def unlock_tui(self):
        syscall(302)
        
    def shutdown(self):
        syscall()