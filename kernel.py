import pickle
import stat
from time import time, sleep
from enum import Enum
from typing import Any
import pygame

from subsystems.qadbio import QaDBIO
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
        self.time = time()
        self.error = string
    def __str__(self) -> str:
        return self.error

def generate_error(exception_type: str, message: str, module: str = "kernel") -> Error:
    timestamp = time()
    fake_exception = f"[MOS/{module}] {exception_type}: {message} (at 0x{timestamp:.0f})"
    return Error(fake_exception)

#
# Red Screen of Death
#

def show_rsod(ks: KernelState, screen: pygame.Surface) -> None:
    if ks.bsod_counter < 10:
        return
    else:
        pygame.mouse.set_visible(False)
        ks.rsod = True

    mr = MimirRender(screen)
    mr.background_color = (64, 0, 0) # pyright: ignore[reportAttributeAccessIssue]

    texts = [
        "MOS has encountered multiple critical error.",
        "The Kernel has been stopped to prevent further damage.",
        "Please reset this installation.",
        f"Error: {str(ks.last_state.bsod_error)}", # pyright: ignore[reportOptionalMemberAccess]
        "Press ESC to shut down."
    ]

    font_size = 32
    line_height = 50
    font = pygame.font.SysFont(None, font_size)

    total_height = len(texts) * line_height
    start_y = (mr.get_height() - total_height) // 2

    # Textobjekte nur EINMAL erstellen
    for i, text in enumerate(texts):
        text_width = font.size(text)[0]

        x = (mr.get_width() - text_width) // 2
        y = start_y + i * line_height

        mr.create_Text(
            x,
            y,
            text,
            font_size,
            (255, 255, 255)
        )

    # RSOD läuft dauerhaft
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ks.aktive = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ks.aktive = False
                    return

        mr.render()
        pygame.display.flip()

#
# Kernel State Class
#

class KernelState:
    last_state: KernelState
    errors: list[Error]
    mode: str                       = "TUI"
    aktive: bool                    = True
    shutdown: bool                  = False
    debug_enabled:bool              = False
    rsod: bool                      = False
    bsod_counter: int               = 0
    bsod_error:Error| None          = None

def save_ks(ks:KernelState) -> None:
    ks.last_state = KernelState()
    try:
        with open("generate\\last_ks.bin", "+wb") as f:
            pickle.dump(ks,f)
    except Exception as e:
        print("Error:" + str(e) + " \nwhile Saving the Kernel-State")
    return

def load_last_ks() -> KernelState:
    try:
        with open("generate\\last_ks.bin", "+rb") as f:
            ks = pickle.load(f)
        return ks
    except FileNotFoundError:
        print("No Last Kernel-State Found")
        return KernelState()
    except Exception as e:
        print("Error:" + str(e) + " \nwhile Saving the Kernel-State")
        return KernelState()

#
# Kernel Mode
#

class KernelMode:
    UI_Mode         :str    = "TUI"
    Debug_Mode      : bool  = False
    Recovery_Mode   : bool  = False

#
# Kernel
#
class Kernel:
    def __init__(self, screen: Any, kernelmode: KernelMode= KernelMode()):
        self.state = KernelState()
        state = self.state

        #Creating Kernel State Externals
        self.errors         = []
        self.aktive         = True
        self.is_shutdown    = False
        self.mode : str     = kernelmode.UI_Mode
        self.debug_mode     = kernelmode.Debug_Mode

        # Giving the State all externals
        state.errors        = self.errors
        state.aktive        = self.aktive
        state.shutdown      = self.is_shutdown
        state.mode          = self.mode
        state.debug_enabled = self.debug_mode

        # Other Kernel Variables
        self.crashdump_req = False
        self.screen: pygame.Surface = screen

        # Subsystems
        self.qadbio:            QaDBIO                      = QaDBIO(self.screen)
        self.gui:               GUI | None
        self.tui:               TextUserInterface | None
        self.debuger:           Debugger | None
        self.logger:            Logger
        self.memoryManager:     MemoryManager
        self.process_manager:   ProcessManager
        self.sheduler:          Sheduler
        self.drivers_manager:   DriverManager
        self.dll_manager:       DLLManager
        self.service_manager:   ServiceManager
        self.syscall_manager:   SyscallManager

        def init(screen: Any) -> None:

            #Setting Up Unchangeable Variables
            self.logger = Logger()

            self.qadbio.show(0)

            if self.debug_mode:
                self.debuger = Debugger(self)


            # Custom System Memory
            self.memoryManager = MemoryManager()

            self.qadbio.show(1)

            if self.mode == "TUI":
                self.tui = TextUserInterface(screen, self.memoryManager)
                self.gui = None
            elif self.mode == "GUI":
                self.tui = None
                self.gui = GUI(screen)
            
            self.qadbio.show(2)

            self.process_manager =      ProcessManager()
            self.sheduler =             Sheduler(self.process_manager.get_process,self.process_manager.run)
            if self.tui:
                self.tui.set_shedueler(self.sheduler)
            if self.gui:
                self.gui.set_shedueler(self.sheduler)

            self.qadbio.show(3)

            self.drivers_manager =      DriverManager()

            self.qadbio.show(4)

            self.dll_manager =          DLLManager()
            self.service_manager =      ServiceManager()

            self.syscall_manager =      SyscallManager(self.memoryManager)

            self.qadbio.show(5)

            self.drivers_manager.load("ntfs")

            self.qadbio.show(6)

            if self.tui:
                self.tui.set_up_syscalls()
            self.drivers_manager.call("ntfs","load_syscalls",self.memoryManager)

            self.sheduler.register_syscalls(self.memoryManager)

            self.add_syscall_subroutines()

            self.syscall_manager.add_syscalls()

            self.qadbio.show(7)

            self.test_system()
            
            self.qadbio.show(8)

            self.logger.log(1,"Start-Up Finished")
            self.load_init_process()
            # for i in range(500):
            #     self.load_init_process(i+10)
            #     self.tui.update()
            self.qadbio.show(100)

            while self.sheduler.runnable():
                self.sheduler.loop()
                if self.tui:
                    self.tui.handle_event()
                if self.gui:
                    self.gui.handle_event()

            #self.shutdown()
            #self.syscall_manager.handle_syscall(1,1024,())
        
        self.state.last_state   = load_last_ks()
        self.state.bsod_counter = self.state.last_state.bsod_counter
        self.state.bsod_error   = self.state.last_state.bsod_error
        print(str(self.state.last_state.bsod_counter) + "\\10")

        self.handle_rsod(kernelmode)

        if not self.state.aktive: return

        

        try:
            init(screen)  
        except KernelException as ke:
            self.crashdump_req = True

            if ke.type == KernelError.NoInitProcess:
                self.errors.append(generate_error("No-Init-Process","No Init Programm found","Kernel-Boot"))
                self.panic(KernelError.NoInitProcess)
                return      
        except Exception as e:
            self.errors.append(generate_error(str(type(e).__name__),"Happend dnw when","Kernel/BOOT"))
            self.crashdump_req = True
            print(e)
            self.panic(KernelError.InitFailed)
            return
        except KeyboardInterrupt as e:
            self.errors.append(generate_error(str(type(e).__name__),"Happend dnw when","Kernel/RUN_TIME"))
            self.crashdump_req = True
            print(e)
            self.panic(KernelError.InitFailed)
            return
        finally:
            self.errors.append(generate_error("KernelException","Happend dnw when","Kernel/RUN_TIME"))
            self.crashdump_req = True
            self.panic(KernelError.NoProcess)

    def handle_rsod(self, kernel_mode: KernelMode) -> None:

        if kernel_mode.Recovery_Mode:   return

        show_rsod(self.state,self.screen)

        if not self.state.aktive:
            save_ks(self.state)
            return

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
            self.syscall_manager.add_syscall_subroutine(self.tui.handle_event)
        if self.gui:
            self.syscall_manager.add_syscall_subroutine(self.gui.handle_event)
        pass
        self.memoryManager.write("syscall_mgr",self.memoryManager.gst_ptr + 400,self.shutdown)

    # Kernel Methods

    def test_system(self):
        if self.tui:
            self.syscall_manager.handle_syscall(1,301,())

        ret: SyscallReturn = self.syscall_manager.handle_syscall(1,1,("generate\\test.test","w"))
        self.syscall_manager.handle_syscall(1,4,(ret.value,"Dies ist ein Test."))
        self.syscall_manager.handle_syscall(1,2,ret.value)

        ret: SyscallReturn = self.syscall_manager.handle_syscall(1,1,("generate\\test.test","r"))
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
        dump = f"MOS-Kernel-Crashdump:\nLatest Error:\n{latest_error}\nErrors:\n{errors}\nMemory:\n{txt}"
        with open("generate\\latest-error.crdmp", "w") as f:
            f.write(dump)
        pass

    def panic(self, error:KernelError):
        if self.is_shutdown:
            self.wait(2)
            self.state.bsod_counter = 0
            save_ks(self.state)
            return
        self.state.bsod_counter += 1
        txts: list[str] = [str(error) for error in self.errors]
        print("Errors: ", txts)
        self.state.bsod_error = self.errors[0]

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
        self.wait(.5)
        self.shutdown(1,0)
        self.wait(2)
        save_ks(self.state)

    def shutdown(self, pid, _):
        if pid != 1: return SyscallReturn(SyscallReturnType.Error, 102)
        self.is_shutdown = True
        
        syscall_logs = self.syscall_manager.shutdown()
        if self.tui:
            tui_logs = self.tui.shutdown()
        if self.gui:
            gui_logs = self.gui.shutdown()
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
            if log.priority < 1 and not self.crashdump_req:
                continue
            logs_txt = logs_txt + str(log) + "\n"
        
        with open("generate\\logs.log","w") as f:
            f.write(logs_txt)
        
        print("Shutdown Success")

    def wait(self,adds):
        start = time()

        add = start + adds

        while time() <= add:
            if self.tui:
                self.tui.update()
            if self.gui:
                self.gui.update()


if __name__ == "__main__":
    import pygame

    pygame.init()
    screen = pygame.display.set_mode(Resolutions.R_1080P.value,pygame.FULLSCREEN)

    kernel = Kernel(screen)

    pygame.quit()
