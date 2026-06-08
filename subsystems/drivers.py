
from types import MethodType
from typing import Any
from drivers.Driver import Driver

class DriverManager:
    def __init__(self):
        self.drivers: dict[str,Driver] = {}
        self.calls : dict[str,MethodType] = {}

    def load(self, name: str):
        imp_str = f"from drivers.{name.lower()} import {name.upper()} as drive"
        
        namespace = {}
        exec(imp_str, namespace)
        
        drive = namespace['drive']
        self.drivers.update({name:drive()})
    
    def load_function(self, idx):
        names = self.drivers[idx]
    
    def call(self,driver,function,args) -> Any:
        if driver in self.drivers.keys():
            return self.drivers[driver].run(function, args)
        else:
            return 0
