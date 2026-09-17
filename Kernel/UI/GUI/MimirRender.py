from typing import Any
from dataclasses import dataclass
import pygame


@dataclass
class RenderObj:
    type: str
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    color: tuple = (255, 255, 255)
    text: str = ""
    font_size: int = 24
    pos1: tuple = None # pyright: ignore[reportAssignmentType]
    pos2: tuple = None # pyright: ignore[reportAssignmentType]
    pos3: tuple = None # pyright: ignore[reportAssignmentType]


class MimirRender:
    def __init__(self, screen: pygame.Surface):
        self.screen: pygame.Surface = screen
        self.objs: dict[int, RenderObj] = {}
        self.next_z = 0
        self.background_color = self.get_color(0,5,0)

        self._sorted_keys: list[int] = []
        self._dirty = False
        self._font_cache: dict[int, pygame.font.Font] = {}
        self._text_cache: dict[int, pygame.Surface] = {}

        # FPS Shower
        self.need_tick = False
        self.cap = False
        self.track_max = False
        self.track_min = False
        self.track_avg = False
        self.max_fps = 0
        self.min_fps = float("inf")
        self.all_fps: list[float] = []

    # --- Internal ---

    def _get_font(self, size: int) -> pygame.font.Font:
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.SysFont(None, size)
        return self._font_cache[size]

    def _add_obj(self, obj: RenderObj) -> int:
        z = self.next_z
        self.objs[z] = obj
        self.next_z += 1
        self._dirty = True
        return z

    # --- Render ---

    def render(self):
        self.screen.fill(self.background_color)

        if self._dirty:
            self._sorted_keys = sorted(self.objs.keys())
            self._dirty = False

        for z in self._sorted_keys:
            obj = self.objs[z]
            match obj.type:
                case "rect":
                    pygame.draw.rect(self.screen, obj.color, (obj.x, obj.y, obj.width, obj.height))
                case "circle":
                    pygame.draw.circle(self.screen, obj.color, (obj.x, obj.y), obj.width)
                case "triangle":
                    pygame.draw.polygon(self.screen, obj.color, [obj.pos1, obj.pos2, obj.pos3])
                case "text":
                    if z not in self._text_cache:
                        font = self._get_font(obj.font_size)
                        self._text_cache[z] = font.render(obj.text, True, obj.color)
                    self.screen.blit(self._text_cache[z], (obj.x, obj.y))

        if self.need_tick:
            if self.cap:
                self.clock.tick(self.fps)
            else:
                self.clock.tick()

    def render_fps(self):
        current = self.clock.get_fps()

        if self.track_max:
            self.max_fps = max(self.max_fps, current)
        if self.track_min and current > 0:  
            self.min_fps = min(self.min_fps, current)
        if self.track_avg:
            self.all_fps.append(current)
            if len(self.all_fps) > 2000:
                self.all_fps.pop(0)



        lines = [f"FPS: {int(current)}"]
        if self.track_max:
            lines.append(f"MAX: {int(self.max_fps)}")
        if self.track_min:
            if self.track_min and self.min_fps != float("inf"):
                lines.append(f"MIN: {int(self.min_fps)}")
            elif self.track_min:
                lines.append("MIN: --")
        if self.track_avg and self.all_fps:
            lines.append(f"AVG: {int(sum(self.all_fps) / len(self.all_fps))}")

        line_height = self.fps_font.get_height()
        for i, line in enumerate(lines):
            surface = self.fps_font.render(line, True, (255, 255, 255))
            self.screen.blit(surface, (self.get_width() - surface.get_width(), i * line_height))

    def calc_fps(self):
            current = self.clock.get_fps()
    
            if self.track_max:
                self.max_fps = max(self.max_fps, current)
            if self.track_min and current > 0:  
                self.min_fps = min(self.min_fps, current)
            if self.track_avg:
                self.all_fps.append(current)
    
    
            lines = [f"FPS: {int(current)}"]
            if self.track_max:
                lines.append(f"MAX: {int(self.max_fps)}")
            if self.track_min:
                if self.track_min and self.min_fps != float("inf"):
                    lines.append(f"MIN: {int(self.min_fps)}")
                elif self.track_min:
                    lines.append("MIN: --")
            if self.track_avg and self.all_fps:
                lines.append(f"AVG: {int(sum(self.all_fps) / len(self.all_fps))}")

    # --- API ---

    def update_obj(self, z: int, **kwargs) -> bool:
        if z not in self.objs:
            return False
        obj = self.objs[z]
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        if any(k in kwargs for k in ("text", "color", "font_size")):
            self._text_cache.pop(z, None)
        self._dirty = True
        return True

    def remove_obj(self, z: int):
        if z in self.objs:
            del self.objs[z]
            self._text_cache.pop(z, None)
            self._dirty = True

    def get_obj(self, z: int) -> RenderObj | None:
        return self.objs.get(z, None)

    def get_color(self, r,g,b) -> pygame.Color:
        return pygame.Color((r,g,b))

    # --- Create ---

    def create_Rect(self, x, y, width, height, color) -> int:
        return self._add_obj(RenderObj("rect", x=x, y=y, width=width, height=height, color=color))

    def create_Circle(self, x, y, radius, color) -> int:
        return self._add_obj(RenderObj("circle", x=x, y=y, width=radius, color=color))

    def create_Triangle(self, pos1, pos2, pos3, color) -> int:
        return self._add_obj(RenderObj("triangle", pos1=pos1, pos2=pos2, pos3=pos3, color=color))

    def create_Text(self, x, y, text, font_size, color) -> int:
        return self._add_obj(RenderObj("text", x=x, y=y, text=text, font_size=font_size, color=color))

    # --- Utils ---

    def clear(self):
        self.objs = {}
        self.next_z = 0
        self._sorted_keys = []
        self._text_cache = {}
        self._dirty = False

    def get_height(self) -> int:
        return self.screen.get_height()

    def get_width(self) -> int:
        return self.screen.get_width()

    def set_up_FPS(self, cap=False, fps=60):
        self.clock = pygame.time.Clock()
        if cap:
            self.cap = True
            self.fps = fps
        self.fps_font = pygame.font.SysFont(None, 36)
        self.need_tick = True
        self.max_fps = 0
        self.min_fps = float("inf")
        self.all_fps: list[float] = []

    def set_up_max_FPS(self, cap=False, fps=60):
        self.set_up_FPS(cap, fps)
        self.track_max = True
        self.max_fps = 0

    def set_up_min_FPS(self, cap=False, fps=60):
        self.set_up_FPS(cap, fps)
        self.track_min = True
        self.min_fps = float("inf")

    def set_up_avg_FPS(self, cap=False, fps=60):
        self.set_up_FPS(cap, fps)
        self.track_avg = True
        self.all_fps: list[float] = []

    def set_up_all_FPS(self, cap=False,fps=60):
        self.set_up_avg_FPS(cap,fps)
        self.set_up_max_FPS(cap,fps)
        self.set_up_min_FPS(cap,fps)
    
    def get_last_FPS_stats(self):
        return {
            "min": int(self.min_fps),
            "max": int(self.max_fps),
            "avg": int(sum(self.all_fps) / len(self.all_fps))
        }

    def shutdown(self):
        self.clear()
        self._font_cache = {}


class Animation:
    def __init__(self, renderer: MimirRender, z_indexes: list[int], prop: str, goals: list[float], frames: int, on_done=None):
        """
        renderer  : MimirRender instance
        z_indexes : List of Z-indexes to animate
        prop      : Property to change (e.g. "x", "y", "width")
        goals     : Target value for each Z-index (same order as z_indexes)
        frames    : Number of frames the animation runs over
        on_done   : Optional callback when finished
        """
        assert len(z_indexes) == len(goals), "z_indexes and goals must be the same length"

        self.renderer = renderer
        self.prop = prop
        self.frames = frames
        self.current_frame = 0
        self.on_done = on_done

        # Calculate step size per object
        self.targets: list[dict] = []
        for z, goal in zip(z_indexes, goals):
            obj = renderer.get_obj(z)
            if obj is None:
                continue
            start = getattr(obj, prop)
            self.targets.append({
                "z":         z,
                "goal":      goal,
                "step_size": (goal - start) / frames
            })

    def update(self) -> bool:
        """Returns True when the animation is finished"""
        if self.current_frame >= self.frames:
            return True

        self.current_frame += 1
        is_last = self.current_frame >= self.frames

        for target in self.targets:
            obj = self.renderer.get_obj(target["z"])
            if obj is None:
                continue
            if is_last:
                # Set to exact target value to avoid floating point errors
                setattr(obj, self.prop, target["goal"])
            else:
                current = getattr(obj, self.prop)
                setattr(obj, self.prop, current + target["step_size"])
            # Invalidate text cache if necessary
            if self.prop in ("color", "font_size", "text"):
                self.renderer._text_cache.pop(target["z"], None)
            self.renderer._dirty = True

        if is_last and self.on_done:
            self.on_done()

        return is_last

    @property
    def done(self) -> bool:
        return self.current_frame >= self.frames


class AnimationManager:
    def __init__(self):
        self.animations: list[Animation] = []

    def add(self, renderer: MimirRender, z_indexes: list[int], prop: str, goals: list[float], frames: int, on_done=None):
        self.animations.append(Animation(renderer, z_indexes, prop, goals, frames, on_done))

    def update(self):
        self.animations = [a for a in self.animations if not a.update()]

    def clear(self):
        self.animations = []