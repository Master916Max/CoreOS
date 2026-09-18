from subsystems.memory import MemoryManager
from subsystems.common import SyscallReturnType
from subsystems.common import SyscallReturn
from types import MethodType
import time
import random

from .procees_multi import Process
from .logging import Logger

class Sheduler:
    def __init__(self, get_process: MethodType, run_process: MethodType):
        self.ready_queue: list[int] = []
        self.waiting_queue: list[int] = []
        self.services_queue: list[int] = []
        self.sleeping_queue: dict[float,int] = {}
        self.logger = Logger()

        self.get_process = get_process
        self.run_process = run_process
    
    def register_programm(self, programm: Process, level: int):
        if level > 1:
            self.ready_queue.append(programm.pid)
        else:
            if isinstance(programm, Process):
                self.services_queue.append(programm.pid)
            else:
                self.logger.log(2,"Try to add Single Process as a Service!")
        
    def loop(self):
        pid_to_run = 0
        
        try:
            self.test_for_ruannable()
        except Exception as e:
            pass

        if len(self.ready_queue) != 0:
            pid_to_run = self.ready_queue[0]
            #self.logger.log(1,"Running Pid:" + str(pid_to_run))
            if pid_to_run and not pid_to_run == 0:
                if self.run_process(pid_to_run) == "finished":
                    self.remove_pid(pid_to_run)

    def runnable(self):
        try:
            self.test_for_ruannable()
        except Exception as e:
            pass
        return True if len(self.waiting_queue) != 0 or len(self.ready_queue) != 0 else False

    def test_for_ruannable(self):
        self.update_sleep()
        ready_to_delete = []
        for pid in self.waiting_queue:
            if self.get_process(pid).state == "ready" or self.get_process(pid).state == "running":
                self.ready_queue.append(pid)
                ready_to_delete.append(pid)
        
        for pid in ready_to_delete:
            self.waiting_queue.remove(pid)

        ready_to_delete = []
        for pid in self.ready_queue:
            if self.get_process(pid).state == "waiting":
                self.waiting_queue.append(pid)
                ready_to_delete.append(pid)
        
        for pid in ready_to_delete:
            self.ready_queue.remove(pid)

        ready_to_delete = []
        for pid in self.waiting_queue:
            if self.get_process(pid).state == "terminated":
                ready_to_delete.append(pid)
        
        for pid in ready_to_delete:
            self.waiting_queue.remove(pid)
        
        ready_to_delete = []
        for pid in self.ready_queue:
            if self.get_process(pid).state == "terminated":
                ready_to_delete.append(pid)
        
        for pid in ready_to_delete:
            self.ready_queue.remove(pid)
    
    def block_process(self,pid):
        if pid in self.ready_queue:
            self.ready_queue.remove(pid)
        if pid not in self.waiting_queue:
            self.waiting_queue.append(pid)
    
    def unblock_process(self,pid):
        if pid in self.waiting_queue:
            self.waiting_queue.remove(pid)
        if pid not in self.ready_queue:
            self.ready_queue.append(pid)
        self.get_process(pid).state = "ready"
        
    def remove_pid(self,rpid):
        for pid in self.ready_queue:
            if pid == rpid:
                self.ready_queue.remove(rpid)
                return
        for pid in self.waiting_queue:
            if pid == rpid:
                self.waiting_queue.remove(rpid)
                return
        
    def shutdown(self):
        self.ready_queue: list[int] = []
        self.waiting_queue: list[int] = []
        self.services_queue: list[int] = []

        return self.logger
    
    def send_to_wait(self,pid,args):
        time_to_wait = args // 10 # Calc the add on timestamp to wait

        timestamp = time.time() + time_to_wait

        self.sleeping_queue[timestamp] = pid

        return SyscallReturn(SyscallReturnType.Wait,0)

    def register_syscalls(self,mr:MemoryManager):
        def write(mr:MemoryManager,idx,func):
            mr.write("syscall_mgr", mr.gst_ptr + idx, func)

        write(mr,909,self.send_to_wait)

    def update_sleep(self):
        to_delete = []
        for sleep_until, pid in self.sleeping_queue.items():
            if sleep_until <= time.time():
                to_delete.append(sleep_until)
        
        # Nicht alle auf einmal aufwecken, sondern X pro Frame
        for t in to_delete[:10]:  # max 10 pro Frame
            pid = self.sleeping_queue[t]
            self.get_process(pid).state = "ready"
            del self.sleeping_queue[t]
                
                
