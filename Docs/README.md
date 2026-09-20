# CoreOS Documentation

This documentation describes the current CoreOS architecture and the planned direction of the operating system.

> **Scope:** This documentation combines the stable concepts from `master` with the current kernel restructuring work from `feature/subdeviding-smart`.

The `Docs/` directory is intentionally architecture-focused. Implementation details may change while the project is being developed.

## Documentation Map

### Architecture
- [Architecture](Architecture.md) — overall system design and subsystem boundaries
- [Boot](Boot.md) — bootloader, QDBIOS and kernel startup
- [IPC](IPC.md) — message routing and module registration
- [Process System](Process.md) — processes and process lifecycle
- [System Calls](Syscalls.md) — user/kernel interface
- [Scheduler](Scheduler.md) — process scheduling model
- [Core](Core.md) — memory, errors and permissions
- [UI](UI.md) — QDBIOS, MimirRender, PrismUI and UI runtime

### Planned Systems
- [Drivers](Drivers.md)
- [Filesystem](Filesystem.md)
- [Services](Services.md)
- [Security](Security.md)
- [SDK](SDK.md)
- [Applications](Applications.md)
- [Debugging](Debugging.md)

### Project
- [Roadmap](Roadmap.md)
- [Development](Development.md)

## Current Development Stage

The current branch is focused on subdividing the kernel into independent subsystems.

Current major development sequence:

1. UI runtime
2. First user process
3. System-call infrastructure
4. Scheduler
5. Process lifecycle
6. Permissions and protection
7. Drivers and services
8. Filesystem
9. Init process
10. Public test release

The architecture is experimental and may change significantly before 1.0.0.
