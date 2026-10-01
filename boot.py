import argparse
import pygame
from enum import Enum

from Kernel.main import Kernel, BootConfig

class Resolutions(Enum):
    R_360P  = (640,  360)
    R_480P  = (854,  480)
    R_720P  = (1280, 720)
    R_1080P = (1920, 1080)
    R_1440P = (2560, 1440)
    R_4K    = (3840, 2160)
    R_8K    = (7680, 4320)

    def width(self)  -> int: return self.value[0]
    def height(self) -> int: return self.value[1]

    def to_tuple(self) -> tuple[int, int]: return self.value

    def aspect_ratio(self) -> str:
        w, h = self.value
        from math import gcd
        d = gcd(w, h)
        return f"{w // d}:{h // d}"

    def __str__(self) -> str:
        return f"{self.value[0]}x{self.value[1]}"

def parse_args():
    parser = argparse.ArgumentParser(
        description="MOS Bootloader"
    )

    # Auflösung
    parser.add_argument(
        "--resolution",
        "-r",
        choices=["4k", "2k", "1080p", "720p", "480p", "360p"],
        default="1080p",
        help="Set the display resolution"
    )

    # Fenster / Fullscreen
    parser.add_argument(
        "--window",
        "-w",
        action="store_true",
        help="Start MOS in windowed mode"
    )

    # Debug
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
            "--recovery",
            action="store_true",
            help="Enable Recovery mode"
        )

    return parser.parse_args()


args = parse_args()

resolution = Resolutions.R_1080P.value
match args.resolution:
    case "4k":
        resolution = Resolutions.R_4K.value
    case "2k":
        resolution = Resolutions.R_1440P.value
    case "1080p":
        resolution = Resolutions.R_1080P.value
    case "720p":
        resolution = Resolutions.R_720P.value
    case "480p":
        resolution = Resolutions.R_480P.value
    case "360p":
        resolution = Resolutions.R_360P.value


# Fullscreen ist Standard
fullscreen = not args.window


pygame.init()

screen = pygame.display.set_mode(
    resolution,
    pygame.FULLSCREEN if fullscreen else 0
)

boot_cfg = BootConfig()

boot_cfg.screen = screen
boot_cfg.UI = "TUI"

live_kernel = Kernel()

live_kernel.load(boot_cfg)
live_kernel.run()

pygame.quit()