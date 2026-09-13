from operator import truediv
from typing import Dict
import pygame

from .GUI.MimirRender import MimirRender
from .logging import Logger
from .sheduler import Sheduler
from .common import SyscallReturn,SyscallReturnType
from .memory import MemoryManager, Cell

class TextUserInterface:
    def __init__(self, screen,memory_mgr: MemoryManager, shedueler: Sheduler|None = None):
        self.screen: pygame.Surface = screen
        self.mr: MimirRender = MimirRender(screen)
        self.mr.set_up_all_FPS()
        self.font = pygame.font.SysFont('Arial', 24)
        self.text_color = (255, 255, 255)  # White color
        self.mr.background_color = self.mr.get_color(0, 0, 0)    # Black color

        self.lock = 0
        self.waiting_queue = []
        self.shedueler : Sheduler|None = shedueler

        self.gst_offset = 300
        self.memory_mgr: MemoryManager = memory_mgr

        self.height = self.mr.get_height() // self.font.render("ABC", True, self.text_color).get_height()  # Calculate how many lines can fit on the screen
        self.width = self.mr.get_width() // (self.font.render("ABCDE", True, self.text_color).get_width()//5)   # Calculate how many characters can fit on a line

        self.lines : list[str] = [""] * self.height  # Initialize empty lines

        self.lines[0] = "[Kernel/BOOT] -> Boot Success"  # Initial message

        self.current_line = 1  # Start at the second line for user input
        self.input_aktive = False
        self.input_mode = "line"
        self.input_buffer = ""

        self.need_update = True

        self.logger = Logger()

        self.logger.log(0,"TUI init successful.")
        self.logger.log(0,f"TUI DATA:\nHeight:{self.height}\nWidth:{self.width}\nInput?:{self.input_aktive}")      

    def set_shedueler(self, shedueler: Sheduler):
        self.shedueler = shedueler

    def draw_text(self, text, position):
        self.mr.create_Text(position[0], position[1], text, 24, self.text_color)

    def print_line(self, text, line_number = None):
        self.need_update = True
        self.handle_max_line()
        if line_number is None:
            line_number = self.current_line
        self.lines[line_number] = self.lines[line_number] + text  # Truncate text if it's too long
        self.current_line += 1  # Move to the next line for the next input
        self.update()

    def set_bg(self, color:pygame.color.Color):
        self.mr.background_color = color
    
    def set_fg(self, color:pygame.color.Color):
        self.text_color = color

    def clear(self):
        self.need_update = True
        for idx in range(len(self.lines)):
            self.lines[idx] = ""
        self.current_line = 0

    def update(self):
        if self.need_update or True:
            self.mr.clear()
            for idx, line in enumerate(self.lines):
                self.draw_text(line, (10, idx * self.font.get_height() + 10))
        self.mr.render()
        self.mr.calc_fps()
        pygame.display.flip()
        self.need_update = False
    
    def handle_event(self):
        # Handle all Pygame events here (e.g., keyboard input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if self.input_aktive:
                    if event.key == pygame.K_BACKSPACE:
                        self.input_buffer = self.input_buffer[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.input_aktive = False
                        if self.input_mode == "line":
                            self.shedueler.unblock_process(self.lock) # pyright: ignore[reportOptionalMemberAccess]
                    else:
                        self.input_buffer += event.unicode
                    print(self.input_buffer)
                    if self.input_mode == "char":
                        self.shedueler.unblock_process(self.lock) # pyright: ignore[reportOptionalMemberAccess]

            else:
                continue
        self.update()

    def handle_max_line(self):
        while self.current_line >= self.height:
            self.lines.pop(0)
            self.lines.append("")
            self.current_line -= 1
            self.need_update = True

    # Syscalls

    def require_tui(self, pid,args):
        if self.lock == 0:
            self.lock = pid
            return SyscallReturn(SyscallReturnType.Succes, 0)
        else:
            self.waiting_queue.append(pid)
            self.shedueler.block_process(pid) # pyright: ignore[reportOptionalMemberAccess]
            return SyscallReturn(SyscallReturnType.Wait,0)

    def unlock_tui(self, pid,args):
        if self.lock == pid:
            self.lock = 0
            return SyscallReturn(SyscallReturnType.Succes, 0)
        else:
            return SyscallReturn(SyscallReturnType.Error,-3)
    
    def update_waiting_queue(self):
        if self.lock == 0 and len(self.waiting_queue) > 0:
            next_pid = self.waiting_queue[0]
            if self.require_tui(next_pid).type == SyscallReturnType.Succes: # pyright: ignore[reportCallIssue]
                self.waiting_queue.remove(next_pid)
                self.shedueler.unblock_process(next_pid) # pyright: ignore[reportOptionalMemberAccess]
                                                
    def print(self,pid, text):
        if pid == self.lock:
            self.print_line(text)
            self.handle_event()
            return SyscallReturn(SyscallReturnType.Succes, 1)

    def read_char(self,pid, _):
        if pid == self.lock:
            if self.input_aktive: return SyscallReturn(SyscallReturnType.Error, "")
            self.input_aktive = True
            self.input_mode = "char"
            self.input_buffer = ""
            self.shedueler.block_process(pid) # pyright: ignore[reportOptionalMemberAccess]
            return SyscallReturn(SyscallReturnType.Wait, self.input_buffer)

    def read_line(self,pid, _):
        if pid == self.lock:
            if self.input_aktive: return SyscallReturn(SyscallReturnType.Error, "")
            self.input_aktive = True
            self.input_mode = "line"
            self.input_buffer = ""
            self.shedueler.block_process(pid) # pyright: ignore[reportOptionalMemberAccess]
            return SyscallReturn(SyscallReturnType.Wait, self.input_buffer)

    def set_up_syscalls(self):
        pass
        def write(self,syscall_id,func):
            self.memory_mgr.write("syscall_mgr",self.memory_mgr.gst_ptr + syscall_id,func)
        
        write(self,301,self.require_tui)
        write(self,302, self.unlock_tui)
        write(self,304,self.print)
        write(self,321,self.read_char)
        write(self,322,self.read_line)
    
    def shutdown(self):
        self.clear()
        self.print_line("System-Shutting-down")
        self.print_line("Please Wait")

        self.handle_event()

        print(self.mr.get_last_FPS_stats())

        return self.logger