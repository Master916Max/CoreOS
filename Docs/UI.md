# User Interface

## UI Architecture

The UI subsystem contains the rendering and user-interface layers.

```text
UI
├── QDBIOS
├── MimirRender
├── PrismUI
├── GUI
└── TUI
```

## QDBIOS

Temporary boot-status output used before normal UI startup.

## MimirRender

Current rendering abstraction above Pygame.

It handles concepts such as:

- rendering
- text
- display
- FPS measurement
- basic graphical output

Current QDBIOS tests show very high rendering performance at common resolutions, so renderer optimization is not currently a major priority.

## PrismUI

Higher-level UI framework under development.

Planned responsibilities:

- widgets
- windows
- input
- layout
- application UI
- interaction

## UI Runtime

The next major UI milestone is a proper runtime loop that can coexist with kernel and process execution without exposing kernel internals directly to UI code.
