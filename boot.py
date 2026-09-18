import argparse
import pygame
from Kernel.kernel import Resolutions

from Kernel.main import Kernel, BootConfig


def parse_args():
    parser = argparse.ArgumentParser(
        description="MOS Bootloader"
    )

    # Auflösung
    parser.add_argument(
        "--resolution",
        "-r",
        choices=["4k", "2k", "1080p", "720p", "480p", "360p"],
        default="360p",
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

resolution = Resolutions.R_360P.value

# Auflösung auswählen
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

live_kernel = Kernel()

live_kernel.load(boot_cfg)
live_kernel.run()

pygame.quit()