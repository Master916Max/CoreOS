# Inter-Process Communication

## Purpose

IPC is the communication layer between CoreOS modules and eventually between processes, services and kernel components.

## Message Model

A message currently contains:

- sender
- receiver
- message ID
- body
- answer-required state

Responses preserve the original message ID.

## Routing

```text
Sender
  │
  ▼
IPC Router
  │
  ├── Validate header
  ├── Find registered module
  └── Queue message
          │
          ▼
       Receiver
          │
          ▼
       Response
```

## Module Registration

Modules register a message queue with IPC.

This allows modules to communicate without storing direct references to unrelated modules.

Current conceptual modules include:

- Kernel
- IPC
- Memory
- Syscall Manager
- TUI

## Planned Improvements

- Safer queue consumption
- Better request/response correlation
- Explicit message types
- More complete validation
- Process-to-process communication
- Timeouts and failure handling
- Better error propagation
- Removal/cleanup of consumed messages

## Important Rule

IPC messages should contain serializable data and identifiers, not direct Python functions or subsystem objects.
