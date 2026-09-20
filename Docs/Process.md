# Process System

## Goal

The process subsystem manages process creation, execution, lifecycle and termination.

## Planned Structure

```text
Process/
├── main.py
├── ProcessMulti_K.py
└── ProcessMulti_U.py
```

- **ProcessMulti_K** — kernel-side process management
- **ProcessMulti_U** — user-side process execution

## Isolation

A user process should not receive direct references to kernel subsystems.

Instead:

```text
User Process
     │
     ├── Syscall
     └── IPC
           │
           ▼
         Kernel
```

## Lifecycle

Planned states include:

- CREATED
- READY
- RUNNING
- WAITING
- STOPPED
- TERMINATED

## Planned Features

- process creation
- process IDs
- process state
- process communication
- syscall requests
- process termination
- resource ownership
- exit codes
- integration with scheduler
