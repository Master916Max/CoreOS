from typing import Any
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
