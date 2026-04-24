from typing import IO, Any

from .Driver import Driver, Invalid_Mode
from .common import SyscallReturn, SyscallReturnType


class NTFS(Driver):
    def __init__(self):
        import os
        self.os = os

        self.next_fd_id = 2

        super().__init__()
        self.files: dict[int,IO] = {}
        self.wd: dict[int, str] = {}

        #
        # Function Specific Values
        #

        self.file_modes = ["r","w","a","rb","wb"]

    def open(self,path, mode):
        if not mode in self.file_modes:
            raise Invalid_Mode
        file = open(path, "rw+")
        self.files.update({self.next_fd_id:file})
        self.next_fd_id += 1
        return self.next_fd_id - 1

    def close(self,id):
        self.files[id].close()
        return 0
    
    def read(self,id,size):
        return self.files[id].read(size)
    
    def write(self,id,data):
        self.files[id]
        return 0
    
    def seek(self,id,offset,whence):
        self.files[id].seek(offset, whence)
        return 0

    def tell(self,id):
        return self.files[id].tell()

    def get_functions(self) -> list[str]:
        return ["open","close","read","write","seek","tell"]
    
    def run(self,function, arg1:int|str,arg2:int|str|None,arg3:None|int) -> Any:
        match function:
            case "open":
                return SyscallReturn(SyscallReturnType.Succes, self.open(arg1, arg2))
            case "close":
                return SyscallReturn(SyscallReturnType.Succes, self.close(arg1))
            case "write":
                return SyscallReturn(SyscallReturnType.Succes, self.write(arg1, arg2))
            case "read":
                return SyscallReturn(SyscallReturnType.Succes, self.read(arg1,arg2))
            case "seek":
                return SyscallReturn(SyscallReturnType.Succes, self.seek(arg1,arg2,arg3))
            case "tell":
                return SyscallReturn(SyscallReturnType.Succes, self.tell(arg1))
            case _ :
                return False
        
    def run_safe(self,function,arg1,arg2= None,arg3=None):
        try:
            return self.run(function,arg1,arg2,arg3)
        except FileExistsError:
            return -20
        except IsADirectoryError:
            return -21
        except NotADirectoryError:
            return -22
        except FileNotFoundError:
            return -23
        except Invalid_Mode:
            return -24
            
