from dataclasses import dataclass
import pygame
from .MimirRender import MimirRender
from.constants import Colors


@dataclass
class UIObj:
    type :str
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    text_color: tuple = Colors.TEXT.to_tuple()
    button_color: tuple = Colors.BUTTON_FACE.to_tuple()


class PrismUI:
    def __init__(self,screen):
        self.mr = MimirRender(screen)
        self.content: dict[str,UIObj] = {}
        self.event_handles: dict[str, callable] = {}
        self.event_handle_mode = "divided"
    
    def register_event_handler(self,event: str,func:callable):
        if event == "all":
            self.event_handle_mode = "single"
            self.event_handles[event] = func
        else:
            self.event_handles[event] = func
    
    def create_Button(self,name,text,pos,size,text_color,button_color,corner_radius):
        self.content[name] = UIObj("button", x=pos[0],y=pos[1],width=size[0],height=size[1],text_color=text_color)
    
    def set_background(self,mode:str, color:tuple=Colors.WINDOW_BACKGROUND.to_tuple(),image:str = None):
        if mode == "color":
            self.mr.background_color = color
        else:
            pass
    
    def render(self):
        pass
