# CoreOS SDK

## Status

Planned.

The long-term project is expected to contain a separate SDK repository.

## Goal

Provide application developers with a stable, higher-level interface over kernel system calls.

## Planned Architecture

```text
Application
    ↓
CoreOS SDK
    ↓
Syscall Interface
    ↓
CoreOS Kernel
```

## Emulator

The SDK is planned to include a syscall emulator/compatibility layer so application code can be tested without booting the complete operating system.

## CI

The planned SDK CI environment will test supported Python versions on:

- Ubuntu Latest
- Windows Latest
- macOS Latest

Development builds and public/beta releases are planned separately from kernel releases.
