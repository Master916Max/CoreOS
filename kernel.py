from ast import excepthandler
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
from subsystems.debug import Debugger


class KernelError(Enum):
    NoProcess = 0,
    InitFailed = 1,
    NoInitProcess=2,

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

class KernelException(Exception):
    type : KernelError
    module: str

class Error:
    def __init__(self, string):
        self.time = time.time()
        self.error = string


def generate_error(exception_type: str, message: str, module: str = "kernel") -> Error:
    timestamp = time.time()

    fake_exception = f"[MOS/{module}] {exception_type}: {message} (at 0x{timestamp:.0f})"
    return Error(fake_exception)


class Kernel:
    def __init__(self, screen: Any, debug_mode: bool = False):
        self.crashdump_req = False
        self.errors = []
        self.is_shutdown = False
        self.debug_mode = debug_mode
        self.screen: pygame.Surface
        self.gui: GUI | None
        self.tui: TextUserInterface | None
        self.logger: Logger
        self.mode : str
        self.debuger: Debugger | None
        self.memoryManager: MemoryManager
        self.process_manager: ProcessManager
        self.sheduler: Sheduler
        self.drivers_manager: DriverManager
        self.dll_manager: DLLManager
        self.service_manager: ServiceManager
        self.syscall_manager: SyscallManager

        def init(screen: Any):

            #Setting Up Unchangeable Variables
            self.screen = screen
            self.logger = Logger()
            
            self.mode = "TUI"

            self.QaDBIO(0)

            if self.debug_mode:
                self.debuger = Debugger(self)


            # Custom System Memory
            self.memoryManager = MemoryManager()  # Initialize the memory manager

            self.QaDBIO(1)

            if self.mode == "TUI":
                self.tui = TextUserInterface(screen, self.memoryManager)
                self.gui = None
            elif self.mode == "GUI":
                self.tui = None
                self.gui = GUI(screen)
            
            self.QaDBIO(2)

            self.process_manager =      ProcessManager()
            self.sheduler =             Sheduler(self.process_manager.get_process,self.process_manager.run)
            if self.tui:
                self.tui.set_shedueler(self.sheduler)
            if self.gui:
                self.gui.set_shedueler(self.sheduler)

            self.QaDBIO(3)

            self.drivers_manager =      DriverManager()

            self.QaDBIO(4)

            self.dll_manager =          DLLManager()
            self.service_manager =      ServiceManager()

            self.syscall_manager =      SyscallManager(self.memoryManager)

            self.QaDBIO(5)

            self.drivers_manager.load("ntfs")

            self.QaDBIO(6)

            if self.tui:
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
                if self.tui:
                    self.tui.update()
                if self.gui:
                    self.gui.update()

            self.shutdown()
            #self.syscall_manager.handle_syscall(1,1024,())

        try:
            init(screen)  
        except KernelException as ke:
            
            if ke.type == KernelError.NoInitProcess:
                self.errors.append(generate_error("No-Init-Process","No Init Programm found","Kernel-Boot"))
                self.panic(KernelError.NoInitProcess)
        except Exception as e:
            self.crashdump_req = True
            self.errors.append(Error(e))
            print(e)
            self.panic(KernelError.InitFailed)
            return
        
        self.panic(KernelError.NoProcess)



    def QaDBIO(self, state:int) -> None:
        """
        Quick and Dirty Boot Information Output, give the user the Current State of the Kernel until the First Process is Executed.
        The uses a Temporary MimirRenderer to Output the Information

        Args:
            state (int): The Current State of the Boot Process(Each Number is hardcoded to a specific State, see below)

        State 0: Initializing the Memory Manager\n
        State 1: Initializing the Graphics System\n
        State 2: Initializing the Process Manager and the Sheduler\n
        State 3: Initializing the Drivers Manager\n
        State 4: Initializing the Syscall Manager\n
        State 5: Loading all the Drivers\n
        State 6: Loading all the Syscalls\n
        State 7: Testing the System\n
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
            #del self.print_txt_QaDBIO
            #del self.QaDBIO
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
        
        time.sleep(0.1)

    def print_txt_QaDBIO(self,text) -> None:
        self.tmp_mr.create_Text(0,self.line*self.line_height,text,24,(255,255,255)) 
        self.line += 1
        self.tmp_mr.render()
        pygame.display.flip()

    def get_all_logs(self) -> None:
        self.logs = {}

        syscalls_logs = self.syscall_manager.logger.get_logs()
        process_logs  = self.process_manager.logger.get_logs()
        sheduel_logs  = self.sheduler.logger.get_logs()
        if self.tui:
            tui_logs      = self.tui.logger.get_logs()
        if self.gui:
            gui_logs      = self.gui.logger.get_logs()
            self.logs.update(gui_logs)

        self.logs.update(syscalls_logs)
        self.logs.update(process_logs)
        self.logs.update(sheduel_logs)
        if self.tui:
            self.logs.update(tui_logs) # pyright: ignore[reportPossiblyUnboundVariable]
        
        # Sort dictionary by keys and return values
        self.logs = dict(sorted(self.logs.items()))
    
    def load_init_process(self, i = 0):
        init_code = ""
        try:
            with open("Initial/init.py", "r") as f:
                init_code = f.read()
            self.create_process("Init Process: "+str(i), init_code)
        except FileNotFoundError:
            ek = KernelException()
            ek.type = KernelError.NoInitProcess
            ek.module = "MAIN"
            self.errors.append(generate_error("File Not Found","No Init Programm found","Kernel/BOOT/INIT_LOADER"))
            raise ek
    
    #Needs Export \/
    def create_process(self, name: str, code: str) -> Process:
        process = self.process_manager.create_process(name, code)
        process.setup_namespace(self.syscall_manager)  # Provide access to the syscall manager
        self.sheduler.register_programm(process,5)
        return process
    
    def add_syscall_subroutines(self):
        if self.tui:
            self.syscall_manager.add_syscall_subroutine(self.tui.update)
        if self.gui:
            self.syscall_manager.add_syscall_subroutine(self.gui.update)
        pass

    # Kernel Methods

    def test_system(self):
        if self.tui:
            self.syscall_manager.handle_syscall(1,301,())

        ret: SyscallReturn = self.syscall_manager.handle_syscall(1,1,("test.test","w"))
        self.syscall_manager.handle_syscall(1,4,(ret.value,"Dies ist ein Test."))
        self.syscall_manager.handle_syscall(1,2,ret.value)

        ret: SyscallReturn = self.syscall_manager.handle_syscall(1,1,("test.test","r"))
        file = self.syscall_manager.handle_syscall(1,3,(ret.value,18)).value
        self.syscall_manager.handle_syscall(1,2,ret.value)

        if self.tui:
            self.syscall_manager.handle_syscall(1,302,())

    def generate_dump(self):
        latest_error = self.errors[-1].error if self.errors else "No errors recorded"
        mem = self.memoryManager.memory
        txt = ""
        for cell in mem:
            txt += cell.__str__()
        errors = ""
        for error in self.errors:
            errors += error.error + "\n"
        dump = f"MOS-Kernel-Crashdump:\nLatest Error:\n{latest_error}\n Errors:{errors}\nMemory:\n{txt}"
        with open("latest-error.crdmp", "w") as f:
            f.write(dump)
        pass


    def panic(self, error:KernelError):
        if self.is_shutdown:
            self.wait(1)
            return
        if not self.tui:
            self.tui = TextUserInterface(self.screen, self.memoryManager)
        self.tui.clear()
        self.tui.set_bg((0,0,128)) # pyright: ignore[reportArgumentType]
        self.tui.print_line(        "---------------Kernel-Panic---------------")
        match error:
            case KernelError.NoInitProcess:
                self.tui.print_line("There is no valid INIT Programm!")
            case KernelError.NoProcess:
                self.tui.print_line("There are no Processes to run!")
            case KernelError.InitFailed:
                self.tui.print_line("The Initialization failed.")
        self.tui.print_line(        "---------------Kernel-Panic---------------")
        self.generate_dump()
        self.wait(2)
        self.shutdown()
        self.wait(2)

           
    def shutdown(self):
        self.is_shutdown = True
        
        syscall_logs = self.syscall_manager.shutdown()
        if self.tui:
            tui_logs =     self.tui.shutdown()
        if self.gui:
                   gui_logs =     self.gui.shutdown()
        sheduler_logs =self.sheduler.shutdown()
        memory_logs =  self.memoryManager.shutdown()

        logs = self.logger.get_logs()
        logs.update(syscall_logs.get_logs())
        if self.tui:
            logs.update(tui_logs.get_logs()) # pyright: ignore[reportPossiblyUnboundVariable]
        if self.gui:
            logs.update(gui_logs.get_logs()) # pyright: ignore[reportPossiblyUnboundVariable]
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
            if self.tui:
                self.tui.update()
            if self.gui:
                self.gui.update()


if __name__ == "__main__":
    import pygame

    pygame.init()
    screen = pygame.display.set_mode(Resolutions.R_1080P.value,pygame.FULLSCREEN)

    kernel = Kernel(screen, debug_mode=False)

    pygame.quit()
