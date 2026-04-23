
from typing import Any
from .logging import Logger

#Debug Context
#from subsystems.debug import Debug

class Process:
    def __init__(self, pid: int, name: str):
        self.pid = pid
        self.name = name
        self.state = "ready"  # Possible states: ready, running, waiting, terminated
        self.namespace = {}  # Process-specific namespace for variables and resources
        self.namespace.update({"ret": pid})
        self.code = ""  # Placeholder for the process's code or function to execute
        self.segments = {}  # Code segments split at syscalls
        self.current_segment = 0
    
    def load_code(self, code: str):
        self.code = code
        self.slice_code()  # Split into segments immediately

    def run(self):
        if self.code is not None:
            self.state = "running"
            self.namespace.update({"syscall": self.syscall})
            try:
                self.exec()  # Execute the process's code in its namespace
            except Exception as e:
                print(f"Error in process {self.pid} ({self.name}): {e}")
                self.state = "terminated"
        else:
            print(f"Process {self.pid} ({self.name}) has no code to run.")
    
    def setup_namespace(self, syscall_manager: Any):
        # This method can be expanded to set up the process's namespace with necessary resources
        self.syscall_mgr = syscall_manager  # Example: Provide access to the syscall manager
    
    def syscall(self, syscall_id: int, args):
        if self.syscall_mgr is not None:
            ret = self.syscall_mgr.handle_syscall(syscall_id, args)
            self.namespace["ret"] = ret
            return
        else:
            print(f"Process {self.pid} ({self.name}) has no access to syscalls.")
            return None

    def slice_code(self):
        """Split code at syscall() calls while preserving control flow (loops, if-statements)"""
        if not self.code:
            self.segments = {0: ""}
            self.current_segment = 0
            return
        
        segments_list = []
        current_segment = ""
        lines = self.code.split('\n')
        
        for line in lines:
            if line.lower().find("syscall(") != -1:
                current_segment = current_segment + line + "\n"
                segments_list.append(current_segment)
                current_segment = ""
            else:
                current_segment = current_segment + line + "\n"

        # Add remaining code as final segment
        if current_segment.strip():
            segments_list.append(current_segment)
        
        # Convert list to dict (or empty dict if no segments)
        self.segments = {i: seg for i, seg in enumerate(segments_list)} if segments_list else {0: ""}
        self.current_segment = 0

    def exec(self):
        """Execute next code segment and pause for multitasking"""
        # Safety check
        if not self.segments or self.current_segment not in self.segments:
            self.state = "terminated"
            return
        
        try:
            exec(self.segments[self.current_segment], self.namespace)
        except Exception as e:
            print(f"Error executing segment {self.current_segment} in process {self.pid} ({self.name}): {e}")
            self.state = "terminated"
            return
        
        # Move to next segment
        self.current_segment += 1
        
        # Check if we have more segments
        if self.current_segment >= len(self.segments) + 1:
            self.state = "terminated"
        else:
            self.state = "ready"  # Wait for syscall to complete before next segment

        return  


class ProcessManager:
    def __init__(self):
        self.processes: dict[int, Process] = {}
        self.next_pid = 1  # Start PID from 1

        self.logger = Logger()

    def create_process(self, name: str, code: str) -> Process:
        pid = self.next_pid
        self.next_pid += 1
        process = Process(pid, name)
        process.load_code(code)
        self.processes[pid] = process

        self.logger.log(1, f"Process created: PID={pid}, Name='{name}'")

        return process

    def get_process(self, pid: int) -> Process|None:
        return self.processes.get(pid, None)

    def terminate_process(self, pid: int):
        if pid in self.processes:
            del self.processes[pid]
            #self.logger.log(1, f"Process terminated: PID={pid}")
    
    def run(self,pid: int):
        process = self.get_process(pid)
        if process is not None:
            process.run()
            #self.logger.log(1, f"Process run completed: PID={pid}, State='{process.state}'")
        else:
            print(f"Process with PID {pid} not found.")