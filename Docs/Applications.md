# Applications

## Goal

Applications are intended to run as user processes rather than as direct extensions of the kernel.

## Architecture

```text
Application
    ↓
CoreOS SDK / Runtime
    ↓
Syscalls
    ↓
Kernel
```

Applications should not require direct access to kernel Python objects.

## Distribution

The long-term ecosystem is intended to allow independently developed applications and services to be distributed separately from the CoreOS kernel.

Applications may use the CoreOS SDK to remain independent of internal kernel implementation details.
