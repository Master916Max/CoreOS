# System Calls

## Purpose

System calls are the controlled interface between user processes and kernel functionality.

## Planned Flow

```text
User Process
     │
     │ syscall(id, arguments)
     ▼
Syscall Manager
     │
     ├── Validate structure
     ├── Validate arguments
     ├── Check permissions
     ├── Determine blocking behaviour
     ├── Find target module
     └── Route request
             │
             ▼
            IPC
             │
             ▼
      Kernel Subsystem
             │
             ▼
          Response
```

## Syscall Metadata

The planned registry may contain metadata such as:

- syscall ID
- name
- argument count
- argument types
- validator
- required permissions
- target module
- blocking/non-blocking behaviour
- response type

## Blocking

Not every syscall has the same execution behaviour.

Examples:

- Memory read/write may complete immediately.
- File operations may block.
- Memory allocation may need to wait for available resources.
- Input operations may wait for input.

The scheduler will eventually use this information when managing process states.

## Design Goal

The Syscall Manager should provide a generic dispatch pipeline rather than becoming a monolithic collection of subsystem-specific implementations.
