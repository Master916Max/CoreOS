from typing import Any
from .logging import Logger
from greenlet import greenlet


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

    def load_code(self, code: str):
        self.code = code
        self._gl  = greenlet(self._laufen)

    def setup_namespace(self, syscall_manager: Any):
        self.syscall_mgr = syscall_manager

    def _syscall_handler(self, syscall_id: int, args):
        # Syscall direkt hier verarbeiten – kein Umweg über Kernel nötig
        if self.syscall_mgr:
            ret = self.syscall_mgr.handle_syscall(syscall_id, args)
            self.namespace["ret"] = ret
        # Einen Schritt fertig → zurück zum ProcessManager
        self._mgr_gl.switch()
        return self.namespace.get("ret")

    def _laufen(self):
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
        """Gleiche Schnittstelle wie vorher – Scheduler merkt keinen Unterschied."""
        process: Process | None = self.processes.get(pid)
        if process is None or process.state == "terminated":
            return
        if isinstance(process, Process):
            procc: Process = process
            procc.state = "running"

            # Erster Aufruf: Greenlet starten. Danach: fortsetzen.
            procc._gl.switch()

            # Hier sind wir wieder wenn syscall() aufgerufen wurde oder Prozess fertig ist
            if procc.state != "terminated":
                procc.state = "ready"