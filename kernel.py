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

class KernelError(Enum):
    NoProcess = 0,
    InirFailed = 1,


class Kernel:
    def __init__(self, screen: Any):
        try:
            # Initialize the kernel and set up necessary components
            self.screen = screen
            self.multi_aktive = True
            self.logger = Logger()

            self.system_data = {}

            self.upper_os_get_data()
            #self.print_system_data()

            # Initialize the Subsystems
            self.syscall_manager =      SyscallManager()
            self.process_manager =      ProcessManager()
            self.sheduler =             Sheduler(self.process_manager.get_process,self.process_manager.run)
            self.tui =                  TextUserInterface(screen, self.sheduler)
            self.drivers_manager =      DriverManager()
            self.dll_manager =          DLLManager()
            self.service_manager =      ServiceManager()


            # Seting up the Subsystems Variables

            self.syscall = []
        except Exception as e:
            self.panic(KernelError.InirFailed)
            print(f"Kernel initialization failed: {e}")
        # Seting up the Subsystems
        
        self.drivers_manager.load("ntfs")
        self.add_syscall_subroutines()
        self.load_syscalls()

        # Start the init process
        #self.tui.update()
        self.logger.log(1,"Start-Up Finished")
        self.load_init_process()
        self.load_init_process(3)
        #self.load_init_process(1)
        while self.sheduler.runnable():
            self.sheduler.loop()
            #Run all Subroutines
            
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
                self.syscall_manager.register_syscall(syscall_id + 0, function)  # Syscall IDs start from 1
        except SyscallAllreadyRegisteredException as e:
            print(f"Error loading syscalls: {e}")
    def setup_syscalls(self):
        
        self.syscall_manager.add_file_syscalls(self.drivers_manager.drivers["ntfs"])
        self.syscall_manager.add_tui_syscalls(self.tui)

        def syscall_create_process(args):
            file= args
            if file != "":
                return 1
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

    # Kernel Methodes

    def panic(self, error:KernelError):
        self.tui.print_line("--------Kernel-Panic--------")
        match error:
            case KernelError.NoProcess:
                self.tui.print_line("There are no Processes to run!")
        self.tui.print_line("--------Kernel-Panic--------")
    
    def shutdown(self):
        pass

    def subroutines(self):
        self.tui.update_waiting_queue()
        self.sheduler.test_for_ruannable()

    def upper_os_get_data(self):
        import psutil
        import platform
        cpu_freq = psutil.cpu_freq()
        ram      = psutil.virtual_memory()
        disk     = psutil.disk_usage('/')
        net      = psutil.net_io_counters()
        battery  = psutil.sensors_battery()

        self.system_data = {
            "cpu": {
                "percent":      psutil.cpu_percent(interval=0.1),
                "cores_phys":   psutil.cpu_count(logical=False),
                "cores_logic":  psutil.cpu_count(logical=True),
                "freq_mhz":     round(cpu_freq.current, 1) if cpu_freq else None,
                "freq_max_mhz": round(cpu_freq.max, 1)     if cpu_freq else None,
            },
            "ram": {
                "total_mb":     round(ram.total     / 1024**2, 1),
                "used_mb":      round(ram.used      / 1024**2, 1),
                "available_mb": round(ram.available / 1024**2, 1),
                "percent":      ram.percent,
            },
            "disk": {
                "total_gb":  round(disk.total / 1024**3, 1),
                "used_gb":   round(disk.used  / 1024**3, 1),
                "free_gb":   round(disk.free  / 1024**3, 1),
                "percent":   disk.percent,
            },
            "network": {
                "bytes_sent_mb": round(net.bytes_sent / 1024**2, 2),
                "bytes_recv_mb": round(net.bytes_recv / 1024**2, 2),
                "packets_sent":  net.packets_sent,
                "packets_recv":  net.packets_recv,
            },
            "battery": {
                "percent":  battery.percent          if battery else None,
                "plugged":  battery.power_plugged    if battery else None,
                "secs_left": battery.secsleft        if battery else None,
            },
            "system": {
                "os":       platform.system(),
                "version":  platform.version(),
                "machine":  platform.machine(),
                "python":   platform.python_version(),
                "hostname": platform.node(),
            }
        }
    def print_system_data(self):
        d = self.system_data

        def bar(percent, width=20):
            filled = int(width * percent / 100)
            return f"[{'█' * filled}{'░' * (width - filled)}] {percent:.1f}%"

        print("╔══════════════════════════════════════╗")
        print("║          SYSTEM INFORMATION          ║")
        print("╠══════════════════════════════════════╣")

        # System
        s = d["system"]
        print("║  🖥  SYSTEM                           ║")
        print(f"║  OS       : {s['os']} {s['version'][:20]:<20} ║")
        print(f"║  Hostname : {s['hostname']:<25} ║")
        print(f"║  Machine  : {s['machine']:<25} ║")
        print(f"║  Python   : {s['python']:<25} ║")
        print("╠══════════════════════════════════════╣")

        # CPU
        c = d["cpu"]
        print("║  ⚙  CPU                               ║")
        print(f"║  Cores    : {c['cores_phys']} physical / {c['cores_logic']} logical{'':<8} ║")
        print(f"║  Freq     : {c['freq_mhz']} MHz (max {c['freq_max_mhz']} MHz){'':<3} ║")
        print(f"║  Load     : {bar(c['percent'])}  ║")
        print("╠══════════════════════════════════════╣")

        # RAM
        r = d["ram"]
        print("║  🧠 RAM                               ║")
        print(f"║  {r['used_mb']:.0f} MB / {r['total_mb']:.0f} MB ({r['available_mb']:.0f} MB free){'':<4} ║")
        print(f"║  Usage    : {bar(r['percent'])}  ║")
        print("╠══════════════════════════════════════╣")

        # Disk
        dk = d["disk"]
        print("║  💾 DISK                              ║")
        print(f"║  {dk['used_gb']:.1f} GB / {dk['total_gb']:.1f} GB ({dk['free_gb']:.1f} GB free){'':<4} ║")
        print(f"║  Usage    : {bar(dk['percent'])}  ║")
        print("╠══════════════════════════════════════╣")

        # Network
        n = d["network"]
        print("║  🌐 NETWORK                           ║")
        print(f"║  Sent     : {n['bytes_sent_mb']:.2f} MB ({n['packets_sent']} packets){'':<4} ║")
        print(f"║  Received : {n['bytes_recv_mb']:.2f} MB ({n['packets_recv']} packets){'':<4} ║")
        print("╠══════════════════════════════════════╣")

        # Battery
        b = d["battery"]
        print("║  🔋 BATTERY                           ║")
        if b["percent"] is None:
            print("║  No battery detected                  ║")
        else:
            status = "Plugged in" if b["plugged"] else "On battery"
            secs   = b["secs_left"]
            left   = f"{secs//3600}h {(secs%3600)//60}m" if secs and secs > 0 else "–"
            print(f"║  Status   : {status:<25} ║")
            print(f"║  Time left: {left:<25} ║")
            print(f"║  Charge   : {bar(b['percent'])}  ║")

        print("╚══════════════════════════════════════╝")

if __name__ == "__main__":
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((3840, 2160),pygame.FULLSCREEN)

    kernel = Kernel(screen)

    pygame.quit()
