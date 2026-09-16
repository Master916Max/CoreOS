from enum import Enum

class Colors(Enum):
    # Window
    WINDOW_BACKGROUND      = (212, 208, 200)
    WINDOW_BORDER          = (0,   0,   0  )

    # Titlebar
    TITLEBAR_ACTIVE        = (0,   0,   128)
    TITLEBAR_INACTIVE      = (128, 128, 128)
    TITLEBAR_TEXT_ACTIVE   = (255, 255, 255)
    TITLEBAR_TEXT_INACTIVE = (212, 208, 200)

    # Buttons
    BUTTON_FACE            = (212, 208, 200)
    BUTTON_SHADOW          = (128, 128, 128)
    BUTTON_HIGHLIGHT       = (255, 255, 255)
    BUTTON_DARK_SHADOW     = (64,  64,  64 )
    BUTTON_TEXT            = (0,   0,   0  )

    # Borders
    BORDER_LIGHT           = (255, 255, 255)
    BORDER_DARK            = (64,  64,  64 )

    # Text
    TEXT                   = (0,   0,   0  )
    TEXT_DISABLED          = (128, 128, 128)
    TEXT_SELECTED          = (255, 255, 255)
    TEXT_SELECTED_BG       = (0,   0,   128)

    # Desktop
    DESKTOP                = (0,   128, 128)

    # Scrollbar
    SCROLLBAR              = (212, 208, 200)

    # Tooltip
    TOOLTIP_BG             = (255, 255, 225)
    TOOLTIP_TEXT           = (0,   0,   0  )

    # Menu
    MENU_BG                = (212, 208, 200)
    MENU_TEXT              = (0,   0,   0  )
    MENU_SELECTED_BG       = (0,   0,   128)
    MENU_SELECTED_TEXT     = (255, 255, 255)
    MENU_DISABLED_TEXT     = (128, 128, 128)

    def to_tuple(self) -> tuple[int, int, int]:
        return self.value