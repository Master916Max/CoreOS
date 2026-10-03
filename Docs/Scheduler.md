# Scheduler

## Purpose

The scheduler decides which runnable process receives execution time.

## Planned States

```text
READY ──► RUNNING ──► READY
             │
             ├──► WAITING
             │       │
             │       └──► READY
             │
             └──► TERMINATED
```

## Responsibilities

The scheduler is expected to manage:

- runnable processes
- process priorities
- execution time
- preemption
- waiting processes
- wake-up events
- context/execution transitions

## Relationship With Syscalls

A syscall may cause a process to continue immediately or enter a waiting state.

```text
RUNNING
   │
   │ blocking syscall
   ▼
WAITING
   │
   │ response/event
   ▼
READY
```

## Implementation Direction

The scheduler will be implemented after the process and syscall foundations exist.

The exact scheduling algorithm is intentionally not fixed yet.
