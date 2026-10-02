# Security and Protection

## Goal

CoreOS should eventually prevent processes and services from accessing resources without authorization.

## Planned Areas

- process identity
- permissions
- capabilities
- memory isolation
- syscall authorization
- IPC authorization
- filesystem permissions
- driver access
- service isolation

## Principle

Security checks should not depend solely on individual applications behaving correctly. Kernel-controlled interfaces should enforce important protection boundaries.
