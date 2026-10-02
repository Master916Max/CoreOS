# Drivers

## Status

Drivers are planned and not yet a complete subsystem.

## Goal

Drivers provide controlled access to host or hardware resources without allowing arbitrary components to directly manipulate kernel internals.

## Planned Model

```text
Kernel
  │
  ▼
Driver Manager
  │
  ├── Storage Driver
  ├── Input Driver
  ├── Display Driver
  └── Other Drivers
```

Drivers should communicate with the rest of the OS through defined interfaces and IPC where practical.

## Development Strategy

The first driver implementations may be simulated/fake drivers. This allows the kernel architecture to be tested before real hardware support is attempted.
