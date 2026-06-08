# CoreOS

CoreOS is an experimental operating system project written in Python.

The goal of CoreOS is to explore operating system concepts, graphical user interfaces, rendering systems, and application management in a simple and accessible way.

## Features

* Python-based architecture
* Custom rendering engine (**MimirRender**)
* Custom GUI framework (**PrismUI**)
* Modular system structure
* Application support
* Experimental shell environment

## Components

### MimirRender

MimirRender is the graphics engine of CoreOS. It handles rendering operations and provides a simple abstraction layer above Pygame.

### PrismUI

PrismUI is the graphical user interface framework of CoreOS. It manages user input, widgets, windows, and application interfaces.

### Core Shell

The Core Shell provides command-line interaction with the system and serves as a basic management interface.

## Requirements

* Python 3.10 or newer
* Pygame

Install dependencies:

```bash
pip install pygame
```

## Running CoreOS

```bash
python main.py
```

*(The startup file may vary depending on the current project structure.)*

## Project Status

CoreOS is currently under active development and should be considered experimental software.

## Goals

* Build a complete desktop environment
* Improve PrismUI and MimirRender
* Add more system applications
* Enhance performance and stability
* Learn operating system and software architecture concepts

## License

This project is currently not licensed. All rights reserved unless stated otherwise.
