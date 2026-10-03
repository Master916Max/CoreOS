# System Services

## Status

Services are a planned userspace/kernel-adjacent layer.

## Goal

Move functionality out of the kernel when it does not need to be a kernel mechanism.

Potential services include:

- filesystem services
- networking
- audio
- display management
- logging
- device management
- system configuration

## Isolation

Services should communicate through IPC and system-call interfaces rather than receiving unrestricted kernel references.
