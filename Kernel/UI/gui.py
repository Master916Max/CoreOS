import pygame

from .GUI.MimirRender import MimirRender
from .GUI.desktop import Desktop
from .GUI._layer_s import Layer, LayerManager


class Window:
    def __init__(self, title, owner, size:tuple):
        self.title = title
        self.owner = owner
        self.size = size
        self.content = pygame.Surface(size)

    def draw(self, screen):
        self.mimir_render.render()
        screen.blit(self.content, (0,0))

    def get_screen(self):
        return self.content
    
    def setup_MimirRender(self):
        self.mimir_render = MimirRender(self.content)

    pass

class WindowManager:
    pass

class GUI:
    def __init__(self, screen):
        self.screen = screen

        self.layer_mgr = LayerManager(self.screen)

        self.dektop_surface = pygame.Surface(screen.get_size())
        self.layer_mgr.add_layer(Layer(0,self.dektop_surface))

        self.window_manager = WindowManager()
        self.desktop = Desktop(self.dektop_surface)

        self.height = self.screen.get_height()
        self.width = self.screen.get_width()

        self.need_update = True

        self.logger = Logger()
        self.logger.log(0,"GUI init successful.")
        self.logger.log(0,f"GUI DATA:\nHeight:{self.height}\nWidth:{self.width}")    

    def draw(self):
        pass

    def handle_input(self, input):
        pass

    def log(self, message):
        pass

    def set_shedueler(self, shedueler: Sheduler):
            self.shedueler = shedueler

    def update(self):
        if self.need_update:
            pass
        self.desktop.render()

        self.layer_mgr.render()
        pygame.display.flip()
        self.need_update = False
    
    def handle_event(self):
        # Handle all Pygame events here (e.g., keyboard input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            else:
                continue
        self.update()

    # Syscalls

    def set_up_syscalls(self):
        pass
    
    def shutdown(self):
        self.update()
        self.logger.log(1,str(self.desktop.get_stats()))
        return self.logger