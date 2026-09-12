import pygame
import kernel
import pygame

def menu(str_l: list[str]) -> int:
    print_txt = "--Select-Resolution--"
    for i, str in enumerate(str_l):
        print_txt = print_txt + f"\n{i})-{str}"
    
    print(print_txt)
    return int(input())
try:
    sel = menu(["4K","2K","1080P","720P","480P","360P",])
except Exception as e:
    print(e)
    print("Select Lowest Resolution as Default")
    sel = 5

resolution = ()

match sel:
    case 0:
        resolution = kernel.Resolutions.R_4K.value
    case 1:
        resolution = kernel.Resolutions.R_1440P.value
    case 2:
        resolution = kernel.Resolutions.R_1080P.value
    case 3:
        resolution = kernel.Resolutions.R_720P.value
    case 4:
        resolution = kernel.Resolutions.R_480P.value
    case 5:
        resolution = kernel.Resolutions.R_360P.value
    case _:
        resolution = kernel.Resolutions.R_360P.value
    
try:
    sel = menu(["Fullscreen","Window"])
except Exception as e:
    print(e)
    print("Select Window as Default")
    sel = 1

fullscreen = True

match sel:
    case 0:
        fullscreen = True
    case 1:
        fullscreen = False

try:
    sel = menu(["Debug_Mode","Normal_Mode"])
except Exception as e:
    print(e)
    print("Select Normal_Mode as Default")
    sel = 1

debug = True

match sel:
    case 0:
        debug = True
    case 1:
        debug = False

pygame.init()
screen = pygame.display.set_mode(resolution,pygame.FULLSCREEN if fullscreen else 0)

live_kernel = kernel.Kernel(screen, debug_mode=debug)

pygame.quit()