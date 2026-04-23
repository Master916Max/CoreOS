import time
from enum import Enum
from typing import Any

from subsystems.syscall import SyscallManager, SyscallAllreadyRegisteredException
from subsystems.tui import TextUserInterface
from subsystems.procees_multi import ProcessManager, Process
from subsystems.sheduler import Sheduler
from subsystems.logging import Logger
from subsystems.drivers import DriverManager
from subsystems.dlls import DLLManager
from subsystems.services import ServiceManager

#Debug Context
from subsystems.debug import Debug

class KernelError(Enum):
    NoProcess = 0

class Kernel:
    def __init__(self, screen: Any):
        # Initialize the kernel and set up necessary components
        self.screen = screen
        self.multi_aktive = True
        self.logger = Logger()


        # Initialize the Subsystems
        self.syscall_manager =      SyscallManager()
        self.process_manager =      ProcessManager()
        self.sheduler =             Sheduler(self.process_manager.get_process,self.process_manager.run)
        self.tui =                  TextUserInterface(screen)
        self.drivers_manager =      DriverManager()
        self.dll_manager =          DLLManager()
        self.service_manager =      ServiceManager()


        # Seting up the Subsystems Variables

        self.syscall = []

        # Seting up the Subsystems
        
        self.add_syscall_subroutines()
        self.load_syscalls()

        # Start the init process
        #self.tui.update()
        self.logger.log(1,"Start-Up Finished")
        self.drivers_manager.load("ntfs")
        self.load_init_process()
        #self.load_init_process(1)
        while self.sheduler.runnable():
            self.sheduler.loop()
            
        self.panic(KernelError.NoProcess)

        self.get_all_logs()
        for log in self.logs.values():
            print(log)


        pygame.time.wait(5000)
        #!ignore
    
    def get_all_logs(self):
        self.logs = {}

        syscalls_logs = self.syscall_manager.logger.get_logs()
        process_logs  = self.process_manager.logger.get_logs()
        sheduel_logs  = self.sheduler.logger.get_logs()
        tui_logs      = self.tui.logger.get_logs()

        self.logs.update(syscalls_logs)
        self.logs.update(process_logs)
        self.logs.update(sheduel_logs)
        self.logs.update(tui_logs)
        
        # Sort dictionary by keys and return values
        self.logs = dict(sorted(self.logs.items()))
    
    def load_init_process(self, i = 0):
        init_code = ""
        with open("Initial/init.py", "r") as f:
            init_code = f.read()
        self.create_process("Init Process: "+str(i), init_code)
    
    #Needs Export \/
    def load_syscalls(self):
        self.setup_syscalls()
        # Load the syscalls into the syscall manager
        try:
            for syscall_id, function in enumerate(self.syscall):
                self.syscall_manager.register_syscall(syscall_id + 1, function)  # Syscall IDs start from 1
        except SyscallAllreadyRegisteredException as e:
            print(f"Error loading syscalls: {e}")
    def setup_syscalls(self):
        
        self.syscall_manager.add_file_syscalls(self.drivers_manager.drivers["ntfs"])

        def syscall_create_process(args):
            file= args["path"]
            if file != "":
                fhid = self.syscall_manager.handle_syscall(1,file)
                code = self.syscall_manager.handle_syscall(3,(fhid, -1))
                process = self.create_process("IDK",str(code))
                return process.pid

        self.syscall.append(syscall_create_process)
    def create_process(self, name: str, code: str) -> Process:
        process = self.process_manager.create_process(name, code)
        process.setup_namespace(self.syscall_manager)  # Provide access to the syscall manager
        self.sheduler.register_programm(process,5)
        return process      
    def add_syscall_subroutines(self):
        self.syscall_manager.add_syscall_subroutine(self.tui.update)
        #self.syscall_manager.add_syscall_subroutine(print)
        # This method can be expanded to include more complex syscall subroutines
        pass


    def panic(self, error:KernelError):
        self.tui.print_line("--------Kernel-Panic--------")
        match error:
            case KernelError.NoProcess:
                self.tui.print_line("There are no Processes to run!")
        self.tui.print_line("--------Kernel-Panic--------")
    
    def shutdown(self):
        pass




if __name__ == "__main__":
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    kernel = Kernel(screen)

    pygame.quit()
