from enum import Enum
from typing import Any

class SystemLevel(Enum):
    User = 3,
    Services = 2,
    Drivers = 1,
    Kernel = 0

class DLL:
    def __init__(self, name: str, level: SystemLevel):
        self.name = name
        self.level = level
        self.loaded = False

    def load(self):
        if not self.loaded:
            print(f"Loading DLL: {self.name} at level {self.level.name}")
            self.loaded = True
        else:
            print(f"DLL {self.name} is already loaded.")

    def unload(self):
        if self.loaded:
            print(f"Unloading DLL: {self.name}")
            self.loaded = False
        else:
            print(f"DLL {self.name} is not loaded.")