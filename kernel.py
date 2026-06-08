from time import time
import time
from enum import Enum
from typing import Any
import pygame

from subsystems.syscall import SyscallManager
from subsystems.common import SyscallReturn, SyscallReturnType
from subsystems.tui import TextUserInterface
from subsystems.gui import GUI
from subsystems.procees_multi import ProcessManager, Process
from subsystems.sheduler import Sheduler
from subsystems.logging import Logger
from subsystems.drivers import DriverManager
from subsystems.dlls import DLLManager
from subsystems.services import ServiceManager
from subsystems.memory import MemoryManager
from subsystems.GUI.MimirRender import MimirRender


class KernelError(Enum):
    NoProcess = 0,
    InitFailed = 1,


class Resolutions(Enum):
    R_360P  = (640,  360)
    R_480P  = (854,  480)
    R_720P  = (1280, 720)
    R_1080P = (1920, 1080)
    R_1440P = (2560, 1440)
    R_4K    = (3840, 2160)
    R_8K    = (7680, 4320)

    def width(self)  -> int: return self.value[0]
    def height(self) -> int: return self.value[1]

    def to_tuple(self) -> tuple[int, int]: return self.value

    def aspect_ratio(self) -> str:
        w, h = self.value
        from math import gcd
        d = gcd(w, h)
        return f"{w // d}:{h // d}"

    def __str__(self) -> str:
        return f"{self.value[0]}x{self.value[1]}"


class Error:
    def __init__(self, string):
        self.time = time.time()
        self.error = string


def generate_error(exception_type: str, message: str, module: str = "kernel") -> Error:
    timestamp = time.time()

    fake_exception = f"[MOS/{module}] {exception_type}: {message} (at 0x{timestamp:.0f})"
    return Error(fake_exception)


class Kernel:
    def __init__(self, screen: Any):
        self.crashdump_req = False
        self.errors = []
        self.is_shutdown = False
        def init(screen: Any):

            #Setting Up Unchangeable Variables
            self.screen = screen
            self.logger = Logger()
            
            self.mode = "GUI"

            self.QaDBIO(0)

            # Custom System Memory
            self.memoryManager = MemoryManager()  # Initialize the memory manager

            self.QaDBIO(1)

            self.tui = TextUserInterface(screen, self.memoryManager)
            self.gui = GUI(screen)

            self.QaDBIO(2)

            self.process_manager =      ProcessManager()
            self.sheduler =             Sheduler(self.process_manager.get_process,self.process_manager.run)
            self.tui.set_shedueler(self.sheduler)

            self.QaDBIO(3)

            self.drivers_manager =      DriverManager()

            self.QaDBIO(4)

            self.dll_manager =          DLLManager()
            self.service_manager =      ServiceManager()

            self.syscall_manager =      SyscallManager(self.memoryManager)

            self.QaDBIO(5)

            self.drivers_manager.load("ntfs")

            self.QaDBIO(6)

            self.tui.set_up_syscalls()
            self.drivers_manager.call("ntfs","load_syscalls",self.memoryManager)

            self.sheduler.register_syscalls(self.memoryManager)

            self.add_syscall_subroutines()

            self.syscall_manager.add_syscalls()

            self.QaDBIO(7)

            self.test_system()
            
            self.QaDBIO(8)

            self.logger.log(1,"Start-Up Finished")
            self.load_init_process()
            # for i in range(500):
            #     self.load_init_process(i+10)
            #     self.tui.update()
            self.QaDBIO(100)

            while self.sheduler.runnable():
                self.sheduler.loop()
                self.tui.update()
                if self.mode == "GUI":
                    self.gui.update()

            self.shutdown()
            #self.syscall_manager.handle_syscall(1,1024,())

        try:
            init(screen)  
        except Exception as e:
            self.crashdump_req = True
            self.errors.append(Error(e))
            print(e)
            self.panic(KernelError.InitFailed)
            return
        
        self.panic(KernelError.NoProcess)



    def QaDBIO(self, state:int):
        """
        Quick and Dirty Boot Information Output, give the user the Current State of the Kernel until the First Process is Executed.
        The uses a Temporary MimirRenderer to Output the Information

        Args:
            state (int): The Current State of the Boot Process(Each Number is hardcoded to a specific State, see below)

        State 0: Initializing the Memory Manager
        State 1: Initializing the Graphics System
        State 2: Initializing the Process Manager and the Sheduler
        State 3: Initializing the Drivers Manager
        State 4: Initializing the Syscall Manager

        State 5: Loading all the Drivers
        State 6: Loading all the Syscalls
        State 7: Testing the System
        State 8: Handing Graphics Control to the Graphics Subsystem and Starting the Init Process
        """
        if state == 0:
            # Setting up the
            self.tmp_mr = MimirRender(self.screen)
            self.line = 0
            self.line_height = 40
        elif state == 100:
            del self.tmp_mr
            del self.line
            del self.line_height
            self.print_txt_QaDBIO = None
            self.QaDBIO = None
            del self.print_txt_QaDBIO
            del self.QaDBIO
            return
        
        match state:
            case 0:
                self.print_txt_QaDBIO("Initializing Memory Manager...")
            case 1:
                self.print_txt_QaDBIO("Initializing Graphics System...")
            case 2:
                self.print_txt_QaDBIO("Initializing Process Manager and Scheduler...")
            case 3:
                self.print_txt_QaDBIO("Initializing Drivers Manager...")
            case 4:
                self.print_txt_QaDBIO("Initializing Syscall Manager...")
            case 5:
                self.print_txt_QaDBIO("Loading Drivers...")
            case 6:
                self.print_txt_QaDBIO("Loading Syscalls...")
            case 7:
                self.print_txt_QaDBIO("Testing System...")
            case 8:
                self.print_txt_QaDBIO("Handing Graphics Control to the Graphics Subsystem and Starting the Init Process...")
        
        time.sleep(0.25)

    def print_txt_QaDBIO(self,text):
        self.tmp_mr.create_Text(0,self.line*self.line_height,text,24,(255,255,255)) 
        self.line += 1
        self.tmp_mr.render()
        pygame.display.flip()

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
    def create_process(self, name: str, code: str) -> Process:
        process = self.process_manager.create_process(name, code)
        process.setup_namespace(self.syscall_manager)  # Provide access to the syscall manager
        self.sheduler.register_programm(process,5)
        return process      
    
    def add_syscall_subroutines(self):
        self.syscall_manager.add_syscall_subroutine(self.tui.update)
        if self.mode == "GUI":
            self.syscall_manager.add_syscall_subroutine(self.gui.update)
        #self.syscall_manager.add_syscall_subroutine(print)
        # This method can be expanded to include more complex syscall subroutines
        pass

    # Kernel Methods

    def test_system(self):
        self.syscall_manager.handle_syscall(1,301,())

        ret: SyscallReturn = self.syscall_manager.handle_syscall(1,1,("test.test","w"))
        self.syscall_manager.handle_syscall(1,4,(ret.value,"Dies ist ein Test."))
        self.syscall_manager.handle_syscall(1,2,ret.value)

        ret: SyscallReturn = self.syscall_manager.handle_syscall(1,1,("test.test","r"))
        file = self.syscall_manager.handle_syscall(1,3,(ret.value,18)).value
        print("File:" + file)
        self.syscall_manager.handle_syscall(1,2,ret.value)

        self.syscall_manager.handle_syscall(1,302,())

    def generate_dump(self):
        latest_error = self.errors[-1].error if self.errors else "No errors recorded"
        mem = self.memoryManager.memory
        txt = ""
        for cell in mem:
            txt += cell.__str__()
        dump = f"MOS-Kernel-Crashdump:\nMemory:\n{txt}\nLatest Error:\n{latest_error}"
        with open("latest-error.crdmp", "w") as f:
            f.write(dump)
        pass


    def panic(self, error:KernelError):
        if self.is_shutdown:
            self.wait(2)
            return
        self.tui.clear()
        self.tui.set_bg((0,0,128))
        self.tui.print_line(        "---------------Kernel-Panic---------------")
        match error:
            case KernelError.NoProcess:
                self.tui.print_line("There are no Processes to run!")
            case KernelError.InitFailed:
                self.tui.print_line("The Initialization failed.")
        self.tui.print_line(        "---------------Kernel-Panic---------------")
        self.wait(2)
        self.shutdown()
        self.wait(2)

           
    def shutdown(self):
        self.is_shutdown = True
        pass
        
        syscall_logs = self.syscall_manager.shutdown()
        tui_logs =     self.tui.shutdown()
        sheduler_logs =self.sheduler.shutdown()
        memory_logs =  self.memoryManager.shutdown()

        logs = self.logger.get_logs()
        logs.update(syscall_logs.get_logs())
        logs.update(tui_logs.get_logs())
        logs.update(sheduler_logs.get_logs())
        logs.update(memory_logs.get_logs())

        logs_txt = ""

        for timestamp, log in sorted(logs.items()):
            #print(log)
            logs_txt = logs_txt + str(log) + "\n"
        
        with open("logs.log","w") as f:
            f.write(logs_txt)
        
        print("Shutdown Success")

    def wait(self,adds):
        start = time.time()

        add = start + adds

        while time.time() <= add:
            self.tui.update()
            if self.mode == "GUI":
                self.gui.update()


if __name__ == "__main__":
    import pygame

    pygame.init()
    screen = pygame.display.set_mode(Resolutions.R_1080P.value,pygame.FULLSCREEN)

    kernel = Kernel(screen)

    pygame.quit()
