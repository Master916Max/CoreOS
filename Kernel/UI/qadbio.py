from .GUI.MimirRender import MimirRender
from ..common import *
import pygame

class QaDBIO:
    def __init__(self, screen):
        self.mr = MimirRender(screen)
        self.mr.background_color = self.mr.get_color(0,5,0)

    def show(self, bootstate:BootState) -> None:
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

        self.mr.clear()
        
        self.line = 0
        self.line_height = 40

        if bootstate.ipc_loaded:
             self.print_txt_QaDBIO("[KERNEL] -> LOADING IPC Module [✓]")
        else:
             self.print_txt_QaDBIO("[KERNEL] -> LOADING IPC Module")

        if bootstate.core_loaded:
             self.print_txt_QaDBIO("[KERNEL] -> LOADING Core Module [✓]")
        else:
             self.print_txt_QaDBIO("[KERNEL] -> LOADING Core Module")

        if bootstate.process_loaded:
             self.print_txt_QaDBIO("[KERNEL] -> LOADING Process Module [✓]")
        else:
             self.print_txt_QaDBIO("[KERNEL] -> LOADING Process Module")

        if bootstate.ui_loaded:
             self.print_txt_QaDBIO("[KERNEL] -> LOADING UI Module [✓]")
        else:
             self.print_txt_QaDBIO("[KERNEL] -> LOADING UI Module")

            

    def print_txt_QaDBIO(self,text) -> None:
            self.mr.create_Text(0,self.line*self.line_height,text,24,(255,255,255)) 
            self.line += 1

    def update(self)-> None:
            self.mr.render()
            pygame.display.flip()