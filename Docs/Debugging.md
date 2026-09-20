# Debugging

## Goal

Kernel debugging is treated as a first-class development concern because failures can involve multiple interacting subsystems.

## Current / Planned Tools

- Logger
- module-specific logs
- debug mode
- internal state inspection
- kernel panic handling
- recovery mode
- crash diagnostics
- OS debugger

## OS Debugger

The project has an experimental debugger concept for inspecting internal kernel state during development.

The intended interface is separate from normal application execution and should not become a required dependency of production kernel operation.
