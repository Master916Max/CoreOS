
import pygame

from ..Core.common import Logger, Return
from ..IPC.common import Message, Module, RouteFNCType
from .GUI.MimirRender import MimirRender


class TextUserInterface:
    def __init__(self, screen,rout_msg:RouteFNCType):
        self.aktiv = True
        self.screen: pygame.Surface = screen
        self.mr: MimirRender = MimirRender(screen)
        self.mr.set_up_all_FPS()
        self.font = pygame.font.SysFont('Arial', 24)
        self.text_color = (255, 255, 255)  # White color
        self.mr.background_color = self.mr.get_color(0, 0, 0)    # Black color

        self.lock = 0
        self.waiting_queue = []
        
        self.route_msg : RouteFNCType = rout_msg
        self.msg_queue: list[Message] = []

        self.exports = {
            [301,"",self.require_lock]
        }


        self.height = self.mr.get_height() // self.font.render("ABCDE", True, self.text_color).get_height()  # Calculate how many lines can fit on the screen
        self.width = self.mr.get_width() // (self.font.render("ABCDE", True, self.text_color).get_width()//5)   # Calculate how many characters can fit on a line

        self.lines : list[str] = [""] * self.height  # Initialize empty lines

        self.lines[0] = "[Kernel/BOOT] -> Boot Success"  # Initial message

        self.current_line = 1  # Start at the second line for user input
        self.input_aktive = False
        self.input_mode = "line"
        self.input_buffer = ""
        self.do_show_input   = False
        self.pending_input_message: Message | None = None

        self.need_update = True

        self.logger = Logger()

        self.logger.log(0,"TUI init successful.")
        self.logger.log(0,f"TUI DATA:\nHeight:{self.height}\nWidth:{self.width}\nInput?:{self.input_aktive}")      

        reg_msg = Message()
        reg_msg.set_header(Module.TUI,Module.IPC, False)
        reg_msg.set_body({
            "action": "register",
            "module": Module.TUI,
            "queue": self.msg_queue
            })
        self.route_msg(reg_msg)

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

    def print_char(self, text, line_number = None):
            self.need_update = True
            self.handle_max_line()
            if line_number is None:
                line_number = self.current_line
            self.lines[line_number] = self.lines[line_number] + text  # Truncate text if it's too long
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
        if not self.aktiv: return
        if self.need_update:
            self.mr.clear()
            for idx, line in enumerate(self.lines):
                if idx == self.current_line and self.do_show_input:
                    line = line + self.input_buffer
                self.draw_text(line, (10, idx * self.font.get_height() + 10))
        self.mr.render()
        self.mr.calc_fps()
        pygame.display.flip()
        self.need_update = False
    
    def handle_event(self):
        if not self.aktiv: return
        # Handle all MSGs from the queue
        self.handle_msg()

        # Handle all Pygame events here (e.g., keyboard input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.send_msg(Module.KERNEL,{"action":"shutdown"})
                
            elif event.type == pygame.KEYDOWN:
                if self.input_aktive:
                    if self.do_show_input: self.need_update = True
                    if event.key == pygame.K_BACKSPACE:
                        self.input_buffer = self.input_buffer[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.input_mode == "line" and self.do_show_input:
                            self.handle_max_line()
                            self.lines[self.current_line] += self.input_buffer
                            self.current_line += 1
                        self.input_aktive = False
                        if self.pending_input_message is not None:
                            self.route_msg(self.pending_input_message.answer({
                                "action": "return",
                                "return": self.input_buffer
                            }))
                            self.pending_input_message = None
                        self.input_buffer = ""
                    else:
                        self.input_buffer += event.unicode
                    if self.input_mode == "char" and event.key not in (pygame.K_BACKSPACE, pygame.K_RETURN):
                        self.input_aktive = False
                        if self.pending_input_message is not None:
                            self.route_msg(self.pending_input_message.answer({
                                "action": "return",
                                "return": self.input_buffer[-1:]
                            }))
                            self.pending_input_message = None
                        self.input_buffer = ""

            else:
                continue
        self.update()

    def handle_max_line(self):
        while self.current_line >= self.height:
            self.lines.pop(0)
            self.lines.append("")
            self.current_line -= 1
            self.need_update = True

    def handle_msg(self):
        while self.msg_queue:
            msg = self.msg_queue.pop(0)
            if not isinstance(msg, Message) or not isinstance(msg.get_body(), dict):
                continue

            body = msg.get_body()
            action = body.get("action")
            pid = body.get("pid")
            result = None
            error = None

            if action == "require_tui":
                if pid is None:
                    error = "Missing process id"
                elif self.lock == 0 or self.lock == pid:
                    self.lock = pid
                    result = {"locked": True}
                else:
                    if pid not in self.waiting_queue:
                        self.waiting_queue.append(pid)
                    result = {"locked": False, "queued": True}
            elif action == "unlock_tui":
                if pid != self.lock:
                    error = "Process does not own the TUI"
                else:
                    self.lock = self.waiting_queue.pop(0) if self.waiting_queue else 0
                    result = {"locked": False, "owner": self.lock}
            elif action in ("print", "print_c"):
                if pid != self.lock:
                    error = "Process does not own the TUI"
                elif not isinstance(body.get("text"), str):
                    error = "TUI output requires string text"
                else:
                    if action == "print":
                        self.print_line(body["text"])
                    else:
                        self.print_char(body["text"])
                    result = {"written": len(body["text"])}
            elif action in ("read_line", "read_char"):
                if pid != self.lock:
                    error = "Process does not own the TUI"
                elif self.input_aktive:
                    error = "TUI input is already active"
                elif not msg.answer_required:
                    error = "TUI input requires a reply-capable message"
                else:
                    self.input_aktive = True
                    self.input_mode = "line" if action == "read_line" else "char"
                    self.input_buffer = ""
                    self.pending_input_message = msg
            elif action == "show_input":
                if pid != self.lock:
                    error = "Process does not own the TUI"
                else:
                    self.do_show_input = True
                    result = {"visible": True}
            elif action == "hide_input":
                if pid != self.lock:
                    error = "Process does not own the TUI"
                else:
                    self.do_show_input = False
                    result = {"visible": False}
            else:
                error = f"Unsupported TUI action: {action}"

            self.need_update = True
            if msg.answer_required and self.pending_input_message is not msg:
                response = {"action": "return"}
                if error is not None:
                    response["error"] = error
                else:
                    response["return"] = result
                self.route_msg(msg.answer(response))

    def send_msg(self,recv: Module,body:dict) -> None:
        msg = Message()
        msg.set_header(Module.TUI,recv,False)
        msg.set_body(body)
        self.route_msg(msg)

    def setup_syscalls(self) -> Return:

        def register_syscall(self,id,action) -> None:
            TextUserInterface.send_msg(self,Module.SYSCALLMANAGER,{
                "action" : "register_syscall",
                "id" : id,
                "action_s" : action
            })

        register_syscall(self,301,"require_tui")


        return Return(True)
#    def set_up_syscalls(self):
#        pass
#        
#        write(self,301,self.require_tui)
#        write(self,302, self.unlock_tui)
#        write(self,303,self.print_c)
#        write(self,304,self.print)
#        write(self,321,self.read_char)
#        write(self,322,self.read_line)
#        write(self,331,self.show_input)
#        write(self,332,self.hide_input)
#    
    def shutdown(self):
        self.clear()
        self.set_bg(self.mr.get_color(0,0,32))
        self.print_line("System-Shutting-down")
        self.print_line("Please Wait")

        self.handle_event()

        print(self.mr.get_last_FPS_stats())

        return self.logger