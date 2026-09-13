from types import FunctionType, MethodType
from typing import Any
from .logging import Logger
from .memory import MemoryManager

class NoneRegisteredSyscallException(Exception):
    pass

class SyscallErrorException(Exception):
    pass

class SyscallAllreadyRegisteredException(Exception):
    pass

class Syscall:
    def __init__(self, syscall_id: int, function: FunctionType):
        self.syscall_id = syscall_id
        self.function = function
    
    def redirect(self,pid:int, args) -> Any:
        return self.function(pid,args)

class SyscallManager:
    def __init__(self, memory_mgr : MemoryManager):
        self.syscalls: dict[int, Syscall] = {}
        self.logger = Logger()
        self.subroutines = []
        self.memory_mgr: MemoryManager = memory_mgr

    def register_syscall(self, syscall_id: int, function: FunctionType):
        if syscall_id in self.syscalls:
            raise SyscallAllreadyRegisteredException(f"Syscall with ID {syscall_id} is already registered.")
        self.syscalls[syscall_id] = Syscall(syscall_id, function)

    def handle_syscall(self,pid: int, syscall_id: int, args) -> Any:
        if syscall_id in self.syscalls:
            try:
                for subroutine in self.subroutines:
                    subroutine()
                return self.syscalls[syscall_id].redirect(pid,args)
            except Exception as e:
                raise SyscallErrorException(f"Error occurred while handling syscall {syscall_id}: {e}")
        else:
            raise NoneRegisteredSyscallException(f"Syscall with ID {syscall_id} not found.")
    
    def add_syscall_subroutine(self, function: MethodType|FunctionType):
        # This method can be expanded to include more complex syscall subroutines
        self.subroutines.append(function)
        pass
    
    def add_syscalls(self):
        for i in range(1024):
            cont = self.memory_mgr.read("syscall_mgr",self.memory_mgr.gst_ptr + i)
            if cont:
                self.syscalls[i] = Syscall(i,cont)
                self.logger.log(0,str(i))
    
    def shutdown(self) -> Logger:
        self.syscalls = {}
        self.subroutines = []
        self.logger.log(1,"[Shutdown]--Syscall-Mgr Shutdown success")

        return self.logger

