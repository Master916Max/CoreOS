# Development

## Philosophy

CoreOS is developed as an architecture and learning project.

The preferred workflow is:

```text
Understand the concept
        ↓
Design the interface
        ↓
Implement the subsystem
        ↓
Test the subsystem
        ↓
Integrate
        ↓
Refactor
```

## Branch

The current kernel restructuring work is being developed on:

**feature/subdeviding-smart**

## Master vs Feature Branch

The master branch represents the older/stable project direction.

The feature branch contains the newer kernel subdivision and decoupling work.

This documentation describes the combined architectural direction while distinguishing planned components from currently implemented ones.

## Contribution Direction

Contributions and bug fixes are expected to respect the subsystem boundaries and project interfaces.

Implementation details are experimental and may change without preserving internal compatibility before the project reaches a stable release.

## Documentation Rule

Detailed technical documentation belongs in this directory and may evolve independently from the README.
