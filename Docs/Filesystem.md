# Filesystem

## Status

Filesystem support is planned.

## Goal

Provide a stable file and directory abstraction above storage drivers.

## Planned Layers

```text
Applications
     ↓
Filesystem API / Syscalls
     ↓
VFS-like Layer
     ↓
Filesystem Implementation
     ↓
Storage Driver
     ↓
Device / Host Storage
```

## Planned Features

- files
- directories
- paths
- permissions
- handles
- filesystem mounting
- storage drivers
- metadata
- caching

The exact on-disk filesystem format is not finalized.
