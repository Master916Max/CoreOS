from typing import IO, Any

from .Driver import Driver, Invalid_Mode
from .common import SyscallReturn, SyscallReturnType
from .memory import MemoryManager


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

        #raise NotImplementedError("NTFS Driver is not implemented yet.")

    def open(self,pid,args):
        path,mode = args
        if mode in self.file_modes:
            pass
        else:
            pass
            raise Invalid_Mode
        file = open(path, mode)
        self.files.update({self.next_fd_id:file})
        self.next_fd_id += 1
        return SyscallReturn(SyscallReturnType.Succes,self.next_fd_id -1)

    def close(self,pid,args):
        self.files[args].close()
        return SyscallReturn(SyscallReturnType.Succes,0)
    
    def read(self,pid,args):
        id,size = args
        return SyscallReturn(SyscallReturnType.Succes,self.files[id].read(size))
    
    def write(self,pid,args):
        id,data = args
        self.files[id].write(data)
        return SyscallReturn(SyscallReturnType.Succes,0)
    
    def seek(self,pid,args):
        id,offset,whence = args
        self.files[id].seek(offset, whence)
        return SyscallReturn(SyscallReturnType.Succes,0)

    def tell(self,pid,args):
        return SyscallReturn(SyscallReturnType.Succes,self.files[args].tell())

    def get_functions(self) -> list[str]:
        return ["open","close","read","write","seek","tell"]
    
    def run(self,function, args) -> Any:
        match function:
            case "open":
                arg1,arg2 = args
                return SyscallReturn(SyscallReturnType.Succes, self.open(arg1, arg2))
            case "close":
                arg1 = args
                return SyscallReturn(SyscallReturnType.Succes, self.close(arg1))
            case "write":
                arg1,arg2 = args
                return SyscallReturn(SyscallReturnType.Succes, self.write(arg1, arg2))
            case "read":
                arg1,arg2= args
                return SyscallReturn(SyscallReturnType.Succes, self.read(arg1,arg2))
            case "seek":
                arg1,arg2,arg3 = args
                return SyscallReturn(SyscallReturnType.Succes, self.seek(arg1,arg2,arg3))
            case "tell":
                arg1 = args
                return SyscallReturn(SyscallReturnType.Succes, self.tell(arg1))
            case "load_syscalls":
                self.load_syscalls(args)
            case _ :
                return False
        
    def run_safe(self,function,args):
        try:
            return self.run(function,args)
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

    def load_syscalls(self,memoryManager:MemoryManager):

        def write(mr:MemoryManager,id,func):
            mr.write("syscall_mgr",mr.gst_ptr+id,func)

        write(memoryManager,1,self.open)
        write(memoryManager,2,self.close)
        write(memoryManager,3,self.read)
        write(memoryManager,4,self.write)
        write(memoryManager,5,self.seek)
        write(memoryManager,6,self.tell)
            
