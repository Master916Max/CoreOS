from types import MethodType

from .procees_multi import Process
from .logging import Logger

class Sheduler:
    def __init__(self, get_process: MethodType, run_process: MethodType):
        self.ready_queue: list[int] = []
        self.waiting_queue: list[int] = []
        self.services_queue: list[int] = []
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
        
        self.test_for_ruannable()

        if len(self.ready_queue) != 0:
            pid_to_run = self.ready_queue[0]
            #self.logger.log(1,"Running Pid:" + str(pid_to_run))
            if pid_to_run and not pid_to_run == 0:
                self.run_process(pid_to_run)
                self.waiting_queue.append(pid_to_run)
                self.ready_queue.remove(pid_to_run)

    def runnable(self):
        self.test_for_ruannable()
        return True if len(self.waiting_queue) != 0 or len(self.ready_queue) != 0 else False

    def test_for_ruannable(self):
        ready_to_delete = []
        for pid in self.waiting_queue:
            if self.get_process(pid).state == "ready":
                self.ready_queue.append(pid)
                ready_to_delete.append(pid)
        
        for pid in ready_to_delete:
            self.waiting_queue.remove(pid)

        ready_to_delete = []
        for pid in self.ready_queue:
            if self.get_process(pid).state != "ready":
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

