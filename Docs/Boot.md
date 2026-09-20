# Boot System

## Current Boot Flow

```text
boot.py
  │
  ├── Parse arguments
  ├── Select resolution
  ├── Initialize Pygame
  ├── Create display
  └── Create BootConfig
          │
          ▼
       Kernel.load()
          │
          ├── IPC
          └── QDBIOS
          │
          ▼
       Kernel.run()
```

## Planned Boot Flow

```text
Bootloader
    ↓
QDBIOS
    ↓
IPC
    ↓
Core
    ↓
Process System
    ↓
UI
    ↓
Drivers
    ↓
Init Process
    ↓
Normal Runtime
```

The exact order may change as subsystem dependencies become clearer.

## BootConfig

Boot configuration currently contains information such as:

- UI selection
- Display surface
- Debug configuration
- Startup options

Resolution and host display configuration are intended to remain boot-level concerns rather than kernel responsibilities.

## QDBIOS

QDBIOS means **Quick and Dirty Boot Information Output System**.

It is a temporary boot interface that displays module startup status until the normal UI and first user process take control.

Example:

```text
[KERNEL] -> LOADING IPC Module [OK]
[KERNEL] -> LOADING Core Module
[KERNEL] -> LOADING Process Module
[KERNEL] -> LOADING UI Module [OK]
```
