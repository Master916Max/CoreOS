from .constants import Colors
from .MimirRender import MimirRender

class Desktop:
    def __init__(self,screen):
        self.mr = MimirRender(screen)
        self.mr.set_up_all_FPS()
        self.bg = Colors.DESKTOP.to_tuple()
        
    
    def render(self):
        self.mr.background_color = self.bg
        self.mr.render()
        self.mr.calc_fps()

        return

    def get_stats(self):
        return self.mr.get_last_FPS_stats()
