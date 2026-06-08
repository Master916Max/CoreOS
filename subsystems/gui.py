import pygame

from .GUI.MimirRender import MimirRender
from .GUI.desktop import Desktop

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
        self.window_manager = WindowManager()
        self.desktop = Desktop(screen)

    def update(self):
        self.desktop.render()
        pygame.display.flip()
        pass

    def draw(self):
        pass

    def handle_input(self, input):
        pass

    def shutdown(self):
        pass

    def log(self, message):
        pass