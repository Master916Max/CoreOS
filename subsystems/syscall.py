from ast import arg
from itertools import tee
from types import FunctionType, MethodType
from typing import Any
from .logging import Logger

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
    
    def redirect(self, args) -> Any:
        return self.function(args)

class SyscallManager:
    def __init__(self):
        self.syscalls: dict[int, Syscall] = {}
        self.logger = Logger()
        self.subroutines = []

    def register_syscall(self, syscall_id: int, function: FunctionType):
        if syscall_id in self.syscalls:
            raise SyscallAllreadyRegisteredException(f"Syscall with ID {syscall_id} is already registered.")
        self.syscalls[syscall_id] = Syscall(syscall_id, function)

    def handle_syscall(self, syscall_id: int, args) -> Any:
        self.logger.log(1,f"Called Syscall ID: {syscall_id} with: {args}")
        if syscall_id in self.syscalls:
            try:
                for subroutine in self.subroutines:
                    subroutine()
                return self.syscalls[syscall_id].redirect(args)
            except Exception as e:
                raise SyscallErrorException(f"Error occurred while handling syscall {syscall_id}: {e}")
        else:
            raise NoneRegisteredSyscallException(f"Syscall with ID {syscall_id} not found.")
    
    def add_syscall_subroutine(self, function: MethodType|FunctionType):
        # This method can be expanded to include more complex syscall subroutines
        self.subroutines.append(function)
        pass

    def add_file_syscalls(self, driver):
        #Open
        def l_open(path,mode):
            return driver.run("open", path,mode)
        #Close
        def close(args):
            FH = args[0]
            return driver.run("close", FH)
        #Read
        def read(args):
            FH = args[0]
            size = args[1]
            return driver.run("read", FH,size)
        #Write
        def write(args):
            FH = args[0]
            data = args[1]
            return driver.run("write", FH, data)
        #Seek
        def seek(args):
            FH = args[0]
            offset = args[1]
            whence = args[2]
            return driver.run("seek", FH, offset, whence)
        #tell
        def tell(args):
            FH = args[0]
            return driver.run("tell", FH)
        open_sys = Syscall(1,l_open)
        close_sys = Syscall(2,close)
        read_sys = Syscall(3, read)
        write_sys = Syscall(4, write)
        seek_sys = Syscall(5,seek)
        tell_sys = Syscall(6, tell)

        self.syscalls[1] = open_sys
        self.syscalls[2] = close_sys
        self.syscalls[3] = read_sys
        self.syscalls[4] = write_sys
        self.syscalls[5] = seek_sys
        self.syscalls[6] = tell_sys