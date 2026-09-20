# Core Subsystem

The Core subsystem contains fundamental kernel mechanisms.

## Planned Components

```text
Core/
├── main.py
├── memory.py
├── permissions.py
├── errors
└── logger
```

## Memory

The current MemoryManager is an experimental simulated memory system.

Current functionality:

- allocation
- freeing
- reading
- writing
- ownership checks
- bounds checks
- free-block tracking
- free-block merging
- IPC requests

The current memory is a collection of simulated cells rather than real physical memory.

### Future Memory Architecture

```text
Memory Manager
     │
     ├── Allocation
     ├── Ownership
     └── Address Spaces
             │
             ▼
       Virtual Memory
             │
             ├── Pages
             ├── Page Tables
             └── Page Faults
```

Virtual memory is a later milestone.

## Permissions

Permissions are planned as a central protection mechanism.

They will eventually apply to:

- processes
- memory
- system calls
- IPC
- files
- drivers
- services

The exact permission and capability model is not finalized.
