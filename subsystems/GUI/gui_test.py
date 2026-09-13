import pygame
from subsystems.GUI.MimirRender import MimirRender, AnimationManager
import pygame

WIN9X_COLORS = {
    # Window
    "window_background":      (212, 208, 200),
    "window_border":          (0,   0,   0  ),

    # Titlebar
    "titlebar_active":        (0,   0,   128),
    "titlebar_inactive":      (128, 128, 128),
    "titlebar_text_active":   (255, 255, 255),
    "titlebar_text_inactive": (212, 208, 200),

    # Buttons (Minimize, Maximize, Close)
    "button_face":            (212, 208, 200),
    "button_shadow":          (128, 128, 128),
    "button_highlight":       (255, 255, 255),
    "button_dark_shadow":     (64,  64,  64 ),
    "button_text":            (0,   0,   0  ),

    # Borders
    "border_light":           (255, 255, 255),
    "border_dark":            (64,  64,  64 ),

    # Text
    "text":                   (0,   0,   0  ),
    "text_disabled":          (128, 128, 128),
    "text_selected":          (255, 255, 255),
    "text_selected_bg":       (0,   0,   128),

    # Desktop
    "desktop":                (0,   128, 128),

    # Scrollbar
    "scrollbar":              (212, 208, 200),

    # Tooltip
    "tooltip_bg":             (255, 255, 225),
    "tooltip_text":           (0,   0,   0  ),

    # Menu
    "menu_bg":                (212, 208, 200),
    "menu_text":              (0,   0,   0  ),
    "menu_selected_bg":       (0,   0,   128),
    "menu_selected_text":     (255, 255, 255),
    "menu_disabled_text":     (128, 128, 128),
}

pygame.init()

screen = pygame.display.set_mode((3840, 2160),pygame.FULLSCREEN)

center = (screen.get_width()//2,screen.get_height()//2)

mr = MimirRender(screen)
mr.background_color = WIN9X_COLORS["desktop"] # pyright: ignore[reportAttributeAccessIssue]

class Window:
    def __init__(self, size, pos):
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.mr = MimirRender(self.surface)
        self._dirty = True
        self.x, self.y = pos
        self.width, self.height = size
        self.border = self.mr.create_Rect(0, 0, self.width, self.height, WIN9X_COLORS["window_border"])
        self.cube  = self.mr.create_Rect(2, 2, self.width - 4, self.height - 4, WIN9X_COLORS["window_background"])

    def mark_dirty(self):
        self._dirty = True

    def draw(self, screen):
        if self._dirty:
            self.mr.render()
            self._dirty = False
        screen.blit(self.surface, (self.x, self.y))


mr.set_up_all_FPS(True, 99999)

running = True

anim_mgr = AnimationManager()

windows: list[Window] = []

def test(mr:MimirRender,idx):

    for i in range(50):
        windows.append(Window((720,480),(center[0]-360,center[1]-240)))

    mr.set_up_FPS()

    for frame in range(500):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False



        anim_mgr.update()

        mr.clear()
        mr.render()
        for win in windows:
            win.draw(screen)
        mr.render_fps()

        pygame.display.flip()

    print(f"IDX: {idx}{mr.get_last_FPS_stats()}")

for ind in range(25):
    test(mr,ind)