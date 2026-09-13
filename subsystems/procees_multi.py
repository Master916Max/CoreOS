from typing import Any

from subsystems.memory import MemoryManager
from .logging import Logger
from greenlet import greenlet
from .common import SyscallReturn, SyscallReturnType

class Process:
    def __init__(self, pid: int, name: str, manager_greenlet):
        self.pid:int     = pid
        self.name:str    = name
        self.state:str   = "ready"
        self.namespace: dict[str,Any]= {"ret": pid}
        self.code :str   = ""
        self.syscall_mgr = None
        self._mgr_gl     = manager_greenlet
        self._gl         = greenlet()
        self._started    = False
        self.ui_input    = ""
        self._to_load    = ""

    def load_code(self, code: str):
        self.code = code
        self._gl  = greenlet(self._run)

    def setup_namespace(self, syscall_manager: Any):
        self.syscall_mgr = syscall_manager

    def _syscall_handler(self, syscall_id: int, args=None):
        if self.syscall_mgr:
            ret = self.syscall_mgr.handle_syscall(self.pid,syscall_id, args)
            if isinstance(ret, SyscallReturn):
                if ret.type == SyscallReturnType.Succes:
                    self.state = "ready"
                    ret = ret.value
                elif ret.type == SyscallReturnType.Wait:
                    self.state = "waiting"
                    self._mgr_gl.switch()
                    if ret.value == 321: 
                        print("Return: ",self.ui_input)
                        return self.ui_input
                elif ret.type == SyscallReturnType.Error:
                    print(f"Error in syscall {syscall_id} with args {args}: {ret.value}")
                    return None
            self.namespace["ret"] = ret
        self._mgr_gl.switch()
        if self._to_load != "":
            self._load_lib()
        return self.namespace.get("ret")

    def _run(self):
        self.state = "running"
        self.namespace.update({"syscall": self._syscall_handler})
        try:
            exec(self.code, self.namespace)
        except Exception as e:
            print(f"Error in process {self.pid} ({self.name}): {e}")
        self.state = "terminated"
        self._mgr_gl.switch()

    def _load_lib(self):
        exec(self._to_load,self.namespace)

    def add_lib(self, code):
        self._to_load += code

        
class ProcessManager:
    def __init__(self):
        self.processes: dict[int, Process] = {}
        self.next_pid = 1
        self.logger   = Logger()
        self._gl      = greenlet.getcurrent()

    def create_process(self, name: str, code: str) -> Process:
        pid     = self.next_pid
        self.next_pid += 1
        process = Process(pid, name, self._gl)
        process.load_code(code)
        self.processes[pid] = process
        self.logger.log(1, f"Process created: PID={pid}, Name='{name}'")
        return process

    def get_process(self, pid: int) -> Process | None:
        return self.processes.get(pid, None)

    def terminate_process(self, pid: int):
        if pid in self.processes:
            del self.processes[pid]

    def run(self, pid: int):
        process_: Process | None = self.processes.get(pid)
        if process_ is None or process_.state == "terminated":
            return
        if isinstance(process_, Process):
            process: Process = process_
            process.state = "running"
            process._gl.switch()
        
        if process_.state == "terminated":
            self.terminate_process(pid)
            return "finished"

    #
    # Syscalls
    #
    def load_lib(self, pid, name):
        code = ""
        if name == "stfn.lib":
            with open("virtual/fs/stfn.lib", "r") as f:
                code = f.read()

        self.get_process(pid).add_lib(code) # pyright: ignore[reportOptionalMemberAccess]



    def add_syscalls(self, memory_mgr: MemoryManager):
        self.mmr: MemoryManager = memory_mgr
        

        def write(self,id,func):
            self.mmr.write("syscall_mgr",self.mmr.gst_ptr + id,func)

        write(self,141,self.load_lib)