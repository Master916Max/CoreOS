from .constants import Colors
from .MimirRender import MimirRender

class Desktop:
    def __init__(self,screen):
        self.mr = MimirRender(screen)
        self.bg = Colors.DESKTOP.to_tuple()
        
    
    def render(self):
        self.mr.background_color = self.bg
        self.mr.render()

        return
