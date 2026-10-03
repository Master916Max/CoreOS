# CoreOS Architecture

## Purpose

CoreOS is an experimental operating-system architecture project. The Python implementation is used to explore kernel design before a possible future reimplementation in lower-level languages.

## High-Level Layers

```text
Applications
     │
     ▼
CoreOS SDK / Runtime
     │
     ▼
System Calls
     │
     ▼
Kernel
 ┌───┼───────────────────────────────┐
 │   │               │               │
IPC Core          Process            UI
 │   │               │               │
 │ Memory      Scheduler        GUI / TUI
 │ Permissions
 │ Errors
 │
 └────────────── Drivers / Services
```

## Kernel State Isolation

The target design separates subsystem state:

```text
KernelState
├── IPC_State
├── Core_State
├── UI_State
└── Process_State
```

Subsystem functions should receive their own state instead of the complete kernel state wherever practical.

Example:

```python
ipc_loop(IPC_State)
```

This reduces coupling and makes subsystem boundaries explicit.

## Design Principles

- Modules communicate through defined interfaces.
- User processes do not directly access kernel internals.
- IPC carries structured data rather than Python object references.
- Security and permissions are centrally enforced.
- Kernel mechanisms should remain separate from higher-level policy where practical.
- Subsystems should be independently testable.
- Python is currently the experimental implementation language, not necessarily the final implementation language.

## Current Structure

```text
Kernel/
├── main.py
├── common.py
├── IPC/
├── Core/
├── Process/
└── UI/
```
