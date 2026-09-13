from .GUI.MimirRender import MimirRender
import pygame
from time import sleep

class QaDBIO:
    def __init__(self, screen):
        self.mr = MimirRender(screen)
        self.mr.background_color = self.mr.get_color(0,5,0)

    def show(self, state:int) -> None:
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
                self.line = 0
                self.line_height = 40
            elif state == 100:
                del self.mr
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
            
            sleep(0.1)

    def print_txt_QaDBIO(self,text) -> None:
            self.mr.create_Text(0,self.line*self.line_height,text,24,(255,255,255)) 
            self.line += 1
            self.mr.render()
            pygame.display.flip()