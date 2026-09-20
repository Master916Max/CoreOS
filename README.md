# CoreOS

> **Experimental operating-system architecture project written in Python**

CoreOS is a long-term experimental operating system project focused on understanding and implementing operating-system architecture from the ground up.

The current implementation is primarily an **architecture and systems-development environment** rather than a production operating system. Python is intentionally used to make the kernel, IPC, process model, memory management, UI, and other subsystems easy to inspect, change, and experiment with.

The long-term goal is to use the Python implementation to understand the architecture deeply enough that parts of the system can eventually be redesigned and ported to lower-level languages and, much later, real hardware.

---

## Current Development

CoreOS is currently undergoing a major kernel restructuring on the:

**feature/subdeviding-smart**

branch.

The purpose of this branch is to subdivide the kernel into clearer subsystems and reduce direct dependencies between them.

The current architecture is moving toward:

~~~text
                    CoreOS
                       │
                    Kernel
                       │
       ┌───────────────┼────────────────┐
       │               │                │
      IPC             Core              UI
       │               │                │
       │          ┌────┴────┐      ┌────┴────┐
       │        Memory   Permissions  GUI    TUI
       │
       └────────────── Process / Syscalls
~~~

The exact implementation is still changing while the architecture is being developed.

---

## Project Goals

CoreOS is being developed to explore concepts such as:

- Kernel architecture
- Process management
- Scheduling
- Inter-process communication
- System calls
- Memory management
- Permissions and protection
- User/kernel separation
- Drivers and system services
- Filesystems
- Graphical and terminal user interfaces
- Application/runtime interfaces
- Debugging and crash handling
- Modular OS design

The project is intentionally built incrementally. A subsystem is designed, implemented, tested, and then integrated into the larger kernel.

---

# Architecture

## Kernel

The kernel is the central platform of CoreOS.

Its job is to coordinate the system and provide the mechanisms required by processes and system services.

The planned kernel responsibilities include:

- Process lifecycle
- Scheduling
- Memory management
- Permissions
- IPC
- System calls
- Error handling
- Kernel state
- Boot and shutdown
- Communication with drivers and services

The kernel should not directly expose all of its internal components to every process. Communication is intended to happen through defined interfaces, especially IPC and system calls.

---

## Kernel State

The kernel is being separated into subsystem-specific state.

The intended model is:

~~~text
KernelState
├── IPC_State
├── Core_State
├── UI_State
└── Process_State
~~~

Subsystem functions should eventually receive only the state belonging to their subsystem instead of the complete KernelState.

For example:

~~~python
ipc_loop(IPC_State)
~~~

rather than giving IPC access to the entire kernel state.

This is intended to make subsystem boundaries explicit and reduce accidental coupling.

---

# IPC

The **Inter-Process Communication** subsystem is currently one of the most developed parts of the new kernel structure.

It provides message-based communication between kernel modules and, later, processes and services.

The basic model is:

~~~text
Sender
   │
   │ Message
   ▼
IPC Router
   │
   ├── Module registration
   ├── Header validation
   └── Message routing
          │
          ▼
       Receiver
          │
          │ Response
          ▼
       IPC Router
~~~

## Messages

Messages currently contain:

- Sender
- Receiver
- Message ID
- Message body
- Whether an answer is required

A message body is represented as structured data rather than a direct Python function or object reference.

Messages can also create a response using the original message ID.

## Module Registration

Kernel components can register themselves with IPC and provide their own message queue.

This allows modules to communicate through the IPC layer without requiring direct references to one another.

Current module identifiers include components such as:

- Kernel
- Memory
- IPC
- Syscall Manager
- TUI

The module registry is expected to grow as additional kernel components are implemented.

---

# Core

The Core subsystem contains fundamental kernel functionality.

## Memory Manager

The current experimental memory manager provides:

- Allocation
- Freeing memory
- Reading memory
- Writing memory
- Ownership tracking
- Bounds checking
- Free-block tracking
- Adjacent free-block merging
- IPC-based requests

The current implementation uses a simulated memory space consisting of cells.

This is deliberately an abstraction rather than a representation of real physical RAM.

### Planned Memory Development

Future work includes:

- More robust allocation metadata
- Better ownership/handle management
- Virtual memory
- Address spaces
- Page-based allocation
- More realistic process memory isolation

Virtual memory is a later architectural goal and is not yet the primary focus of the current implementation.

## Permissions

Permissions are part of the planned Core architecture.

The long-term goal is to prevent processes and services from directly accessing resources they are not allowed to use.

Permission checks will eventually interact with:

- Processes
- System calls
- IPC
- Memory
- Filesystems
- Drivers
- Services

The permission model is still under development.

---

# Process System

Process management is being designed as an independent kernel subsystem.

The architecture distinguishes between kernel-side process management and user-side process execution.

The current planned structure includes:

~~~text
Process
├── Process Manager
├── Kernel-side process handling
├── User-side process execution
└── Scheduler
~~~

The project uses separate concepts for:

- ProcessMulti_K — kernel-side process management
- ProcessMulti_U — user-side process execution

The intention is that user processes do not directly control kernel subsystems.

Instead, they communicate with the kernel through defined interfaces.

---

# Scheduler

The scheduler is planned as the component responsible for deciding which runnable process receives execution time.

The intended process lifecycle includes states such as:

~~~text
          ┌──────────┐
          │  READY   │
          └────┬─────┘
               │
               ▼
          ┌──────────┐
          │ RUNNING  │
          └────┬─────┘
          │    │    │
       wait   exit  preempt
          │    │    │
          ▼    ▼    └──────► READY
       WAITING
~~~

The scheduler is intentionally being implemented after the process and syscall foundations are established.

---

# System Calls

System calls will provide the controlled interface between user processes and kernel functionality.

The intended architecture is:

~~~text
User Process
     │
     │ System Call
     ▼
Syscall Manager
     │
     ├── Validate request
     ├── Check arguments
     ├── Check permissions
     ├── Determine blocking behaviour
     ├── Find target subsystem
     └── Route request
              │
              ▼
             IPC
              │
              ▼
        Kernel Subsystem
~~~

The Syscall Manager is intended to provide a generic dispatch and validation layer rather than becoming a large collection of subsystem-specific logic.

Some system calls may block, while others can complete immediately.

---

# UI

CoreOS currently contains a developing UI subsystem with separate UI components.

## QDBIOS

**QDBIOS — Quick and Dirty Boot Information Output System** is a temporary boot-status interface.

It displays the state of kernel startup until the normal UI and first user process take over.

Example:

~~~text
[KERNEL] -> LOADING IPC Module [OK]
[KERNEL] -> LOADING Core Module
[KERNEL] -> LOADING Process Module
[KERNEL] -> LOADING UI Module [OK]
~~~

QDBIOS uses a temporary rendering path and is not intended to become the complete CoreOS desktop environment.

## MimirRender

**MimirRender** is the current rendering abstraction built above Pygame.

It provides functionality for:

- Rendering
- Text
- Display handling
- FPS measurement
- Basic graphical output

Current testing shows that the lightweight QDBIOS rendering workload can run at very high frame rates even at 1080p, so renderer optimization is not currently a primary development goal.

## PrismUI

**PrismUI** is intended to become the higher-level graphical UI framework.

Its long-term responsibilities include concepts such as:

- Windows
- Widgets
- Input
- UI layout
- Application interfaces

The UI subsystem is still under active development.

---

# Boot Process

The bootloader is responsible for preparing the host environment before starting the kernel.

The current boot flow is approximately:

~~~text
Bootloader
   │
   ├── Parse command-line options
   ├── Select resolution
   ├── Initialize Pygame
   ├── Create display
   ├── Build BootConfig
   │
   ▼
Kernel.load()
   │
   ├── IPC
   └── QDBIOS
   │
   ▼
Kernel.run()
~~~

The planned boot process will grow as more subsystems are integrated.

The long-term target is approximately:

~~~text
Bootloader
    ↓
QDBIOS
    ↓
IPC
    ↓
Core
    ↓
Process System
    ↓
UI
    ↓
Drivers
    ↓
Init Process
    ↓
Normal Runtime
~~~

The exact order may change as the architecture develops.

---

# OS Layout

CoreOS is intended to separate the kernel platform from the operating-system userspace.

The planned OS-side structure is Linux-inspired while using CoreOS-specific names:

~~~text
OS/
├── Services/
├── Drivers/
├── Libraries/
├── Apps/
├── Home/
├── Temporaries/
└── Config/
~~~

The OS environment is intended to contain the components that are built on top of the kernel.

The long-term design allows the kernel to remain the underlying platform while the OS environment can be assembled and configured separately.

A future first-boot system may allow users to select or obtain components such as:

- UI
- Drivers
- Services
- Applications
- Other OS components

---

# Drivers and Services

Drivers and system services are intended to be isolated from the kernel as much as practical.

The planned architecture is:

~~~text
Kernel
  │
  ├── IPC
  │
  ├── Drivers
  │
  └── Services
        │
        └── Processes / isolated components
~~~

A component should not need direct access to unrelated kernel internals.

Communication should happen through controlled interfaces.

The first driver implementations are expected to be intentionally simple, including experimental/fake drivers used during development before real hardware support is attempted.

---

# SDK and Application Ecosystem

The long-term CoreOS project is planned as more than a single repository.

The intended ecosystem is:

~~~text
┌──────────────────┐
│   CoreOS Kernel  │
└────────┬─────────┘
         │
         │ Syscall Interface
         ▼
┌──────────────────┐
│   CoreOS SDK     │
│                  │
│ Wrappers         │
│ Emulator         │
│ Compatibility    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Applications     │
└──────────────────┘
~~~

The SDK is planned to provide higher-level wrappers around kernel functionality while also allowing applications to be tested against a syscall emulator/compatibility layer.

Applications are intended to be independently developed and released from the kernel itself.

This allows the kernel, SDK, and applications to evolve on separate release cycles.

---

# Debugging

CoreOS is being designed with debugging in mind because kernel failures are difficult to diagnose once multiple subsystems interact.

Planned and experimental debugging functionality includes:

- Kernel logging
- Module-specific logging
- Internal-state inspection
- Debug mode
- Crash handling
- Recovery mode
- Kernel panic handling
- Development debugging interfaces

The project also contains the concept of a dedicated OS debugger for inspecting internal state during development.

---

# Development Philosophy

CoreOS is intentionally developed incrementally.

The current development approach is:

~~~text
Architecture
    ↓
Subsystem
    ↓
Interface
    ↓
Implementation
    ↓
Testing
    ↓
Integration
~~~

The project prioritizes understanding the underlying operating-system concepts over simply producing a working application.

The Python implementation is therefore considered an experimental kernel architecture rather than the final technological form of the operating system.

---

# Current Roadmap

The near-term development order is approximately:

- [x] Initial kernel restructuring
- [x] IPC foundation
- [x] Experimental memory manager
- [x] QDBIOS boot-status output
- [ ] UI runtime loop
- [ ] First user process
- [ ] System-call infrastructure
- [ ] Scheduler
- [ ] Improved process lifecycle
- [ ] Permission system
- [ ] Driver subsystem
- [ ] Init process
- [ ] Basic filesystem support
- [ ] More complete UI
- [ ] Basic system applications
- [ ] SDK and syscall emulator
- [ ] First public test release

This roadmap is not a fixed specification. Architectural decisions may change as the implementation and testing reveal better approaches.

---

# Project Status

CoreOS is **experimental and under active development**.

The current feature branch is focused on restructuring the kernel into more independent subsystems and establishing the interfaces between them.

It should not currently be treated as a production operating system.

The first public test release is planned after the fundamental runtime pieces — UI, process execution, system calls, and scheduling — are working together.

---

# Repository Structure

The current kernel structure is approximately:

~~~text
Kernel/
├── main.py
├── common.py
│
├── IPC/
│   ├── main.py
│   ├── common.py
│   └── ipc.py
│
├── Core/
│   ├── main.py
│   ├── common.py
│   ├── memory.py
│   └── permissions.py
│
├── Process/
│   ├── main.py
│   ├── ProcessMulti_K.py
│   └── ProcessMulti_U.py
│
└── UI/
    ├── main.py
    ├── common.py
    ├── qadbio.py
    └── ...
~~~

The structure is actively changing during the current kernel subdivision work.

---

# Requirements

The current implementation is Python-based and uses Pygame for display and rendering.

Typical development requirements include:

- Python 3.x
- Pygame

The exact dependency set may change as CoreOS develops.

---

# Running the Development Version

The current development entry point is the bootloader:

~~~bash
python boot.py
~~~

The bootloader currently supports command-line options for display resolution, windowed mode, debug mode, and recovery mode.

Example:

~~~bash
python boot.py --resolution 1080p
~~~

The command-line interface and startup behaviour are experimental and may change during development.

---

# Versioning

CoreOS is currently in pre-release development.

The first public test version is planned as part of the early 0.x development series.

Version numbers should not be interpreted as an indication that the internal architecture is already stable. Kernel APIs, syscall interfaces, module boundaries, and other internal structures may change substantially before the 1.0.0 milestone.

---

# Documentation

The documentation under **Docs/** is intentionally **not described by this README**.

That documentation is planned to be completely rewritten separately.

This README describes the project and the current architecture at a high level; detailed technical documentation will be maintained independently.

---

# License

CoreOS is currently being developed under a custom licensing model.

The intended license is designed to allow people to:

- Use the official CoreOS code privately
- Modify the code for private use
- Create fixes and improvements
- Contribute improvements back to the official project
- Build separate extensions or applications on top of CoreOS
- Commercially distribute independent extensions or applications

At the same time, redistribution of the original CoreOS source as a new independent project is intended to remain restricted.

The final license text will define these permissions and restrictions precisely.

Until the final license is published, the repository should not be assumed to grant permissions beyond those explicitly stated by the project owner.

---

# Long-Term Vision

The long-term vision of CoreOS is to progress from an experimental Python operating-system architecture toward a much lower-level implementation.

The approximate direction is:

~~~text
Python Architecture
        ↓
Better Kernel Architecture
        ↓
Low-Level Reimplementation
        ↓
C / C++ Components
        ↓
Bootloader + Real Hardware
        ↓
Standalone Operating System
~~~

This is a long-term project and not a short-term compatibility goal.

The Python implementation exists to make the architecture understandable, testable, and changeable before attempting the significantly harder task of implementing the same concepts at a lower level.

---

**CoreOS is an experimental project by Master916Max.**
