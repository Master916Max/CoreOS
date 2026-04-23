# MyPyOS Syscall Reference

**Version**: 1.0  
**Total Syscalls**: ~202  
**Target OS**: Educational Python-based OS  
**Architecture**: POSIX-like with Windows influences

---

## Table of Contents

1. [File I/O & Filesystem](#1-file-io--filesystem) (22)
2. [Process Management](#2-process-management) (32)
3. [GUI/TUI Operations](#3-guitui-operations) (25)
4. [DLL/Module Loading](#4-dllmodule-loading) (15)
5. [Memory Management](#5-memory-management) (8)
6. [Device I/O & Control](#6-device-io--control) (22)
7. [Signals & IPC](#7-signals--ipc) (20)
8. [Threading](#8-threading) (20)
9. [Time Operations](#9-time-operations) (10)
10. [Miscellaneous](#10-miscellaneous) (16)

---

## 1. File I/O & Filesystem

| ID | Syscall | Parameters | Returns | Errors | Scope |
|---|---------|-----------|---------|--------|-------|
| 1 | `open` | `(path: str, mode: str)` | `int (fd)` | `FILE_NOT_FOUND`, `PERMISSION_DENIED`, `INVALID_MODE` | Both |
| 2 | `close` | `(fd: int)` | `int (0=success)` | `INVALID_FD`, `IO_ERROR` | Both |
| 3 | `read` | `(fd: int, size: int)` | `str` | `INVALID_FD`, `IO_ERROR`, `EOF` | Both |
| 4 | `write` | `(fd: int, data: str)` | `int (bytes_written)` | `INVALID_FD`, `IO_ERROR`, `PERMISSION_DENIED` | Both |
| 5 | `seek` | `(fd: int, offset: int, whence: int)` | `int (new_position)` | `INVALID_FD`, `INVALID_OFFSET`, `IO_ERROR` | Both |
| 6 | `tell` | `(fd: int)` | `int (position)` | `INVALID_FD`, `IO_ERROR` | Both |
| 7 | `stat` | `(path: str)` | `dict (file_stats)` | `FILE_NOT_FOUND`, `PERMISSION_DENIED` | Both |
| 8 | `fstat` | `(fd: int)` | `dict (file_stats)` | `INVALID_FD` | Both |
| 9 | `mkdir` | `(path: str, mode: int)` | `int (0=success)` | `PERMISSION_DENIED`, `FILE_EXISTS`, `PATH_NOT_FOUND` | Both |
| 10 | `rmdir` | `(path: str)` | `int (0=success)` | `PERMISSION_DENIED`, `DIR_NOT_EMPTY`, `FILE_NOT_FOUND` | Both |
| 11 | `chdir` | `(path: str)` | `int (0=success)` | `FILE_NOT_FOUND`, `PERMISSION_DENIED`, `NOT_DIRECTORY` | Both |
| 12 | `getcwd` | `()` | `str (current_path)` | `IO_ERROR` | Both |
| 13 | `opendir` | `(path: str)` | `int (dir_fd)` | `FILE_NOT_FOUND`, `NOT_DIRECTORY`, `PERMISSION_DENIED` | Both |
| 14 | `readdir` | `(dir_fd: int)` | `list (entries)` | `INVALID_FD`, `IO_ERROR` | Both |
| 15 | `closedir` | `(dir_fd: int)` | `int (0=success)` | `INVALID_FD`, `IO_ERROR` | Both |
| 16 | `unlink` | `(path: str)` | `int (0=success)` | `FILE_NOT_FOUND`, `PERMISSION_DENIED`, `IS_DIRECTORY` | Both |
| 17 | `rename` | `(old_path: str, new_path: str)` | `int (0=success)` | `FILE_NOT_FOUND`, `PERMISSION_DENIED`, `FILE_EXISTS` | Both |
| 18 | `truncate` | `(path: str, size: int)` | `int (0=success)` | `FILE_NOT_FOUND`, `PERMISSION_DENIED`, `IO_ERROR` | Both |
| 19 | `chmod` | `(path: str, mode: int)` | `int (0=success)` | `FILE_NOT_FOUND`, `PERMISSION_DENIED` | Both |
| 20 | `chown` | `(path: str, uid: int, gid: int)` | `int (0=success)` | `FILE_NOT_FOUND`, `PERMISSION_DENIED` | Both |
| 21 | `access` | `(path: str, mode: int)` | `int (0=yes, -1=no)` | None | Both |
| 22 | `flush` | `(fd: int)` | `int (0=success)` | `INVALID_FD`, `IO_ERROR` | Both |

---

## 2. Process Management

| ID | Syscall | Parameters | Returns | Errors | Scope |
|---|---------|-----------|---------|--------|-------|
| 101 | `create_process` | `(name: str, code: str)` | `int (pid)` | `INVALID_CODE`, `RESOURCE_EXHAUSTED` | Both |
| 102 | `exit` | `(code: int)` | `void` | None | Both |
| 103 | `wait` | `()` | `int (pid)` | `NO_CHILD_PROCESSES` | Both |
| 104 | `waitpid` | `(pid: int)` | `int (status)` | `INVALID_PID`, `NO_CHILD_PROCESSES` | Both |
| 105 | `getpid` | `()` | `int (pid)` | None | Both |
| 106 | `getppid` | `()` | `int (ppid)` | None | Both |
| 107 | `terminate_process` | `(pid: int)` | `int (0=success)` | `INVALID_PID`, `PERMISSION_DENIED` | Both |
| 108 | `kill_process` | `(pid: int, signal: int)` | `int (0=success)` | `INVALID_PID`, `PERMISSION_DENIED` | Both |
| 109 | `getuid` | `()` | `int (uid)` | None | Both |
| 110 | `setuid` | `(uid: int)` | `int (0=success)` | `PERMISSION_DENIED` | Both |
| 111 | `getgid` | `()` | `int (gid)` | None | Both |
| 112 | `setgid` | `(gid: int)` | `int (0=success)` | `PERMISSION_DENIED` | Both |
| 113 | `getgroups` | `()` | `list (gids)` | None | Both |
| 114 | `setgroups` | `(gids: list)` | `int (0=success)` | `PERMISSION_DENIED` | Both |
| 115 | `getpriority` | `(pid: int)` | `int (priority)` | `INVALID_PID` | Both |
| 116 | `setpriority` | `(pid: int, priority: int)` | `int (0=success)` | `INVALID_PID`, `INVALID_PRIORITY` | Both |
| 117 | `nice` | `(increment: int)` | `int (new_priority)` | `INVALID_INCREMENT` | Both |
| 118 | `yield_cpu` | `()` | `int (0=success)` | None | Both |
| 119 | `get_process_env` | `(pid: int)` | `dict (environment)` | `INVALID_PID` | Both |
| 120 | `set_process_env` | `(pid: int, key: str, value: str)` | `int (0=success)` | `INVALID_PID`, `PERMISSION_DENIED` | Both |
| 121 | `getenv` | `(key: str)` | `str (value)` | `ENV_NOT_FOUND` | Both |
| 122 | `setenv` | `(key: str, value: str)` | `int (0=success)` | None | Both |
| 123 | `unsetenv` | `(key: str)` | `int (0=success)` | `ENV_NOT_FOUND` | Both |
| 124 | `get_process_state` | `(pid: int)` | `str (state)` | `INVALID_PID` | Both |
| 125 | `getrusage` | `(pid: int)` | `dict (resource_usage)` | `INVALID_PID` | Both |
| 126 | `get_process_info` | `(pid: int)` | `dict (proc_info)` | `INVALID_PID` | Both |
| 127 | `get_all_pids` | `()` | `list (pids)` | None | Both |
| 128 | `getprocesses` | `()` | `list (process_list)` | None | Both |
| 129 | `get_parent_pid` | `(pid: int)` | `int (ppid)` | `INVALID_PID` | Both |
| 130 | `is_service` | `()` | `int (1=yes, 0=no)` | None | Both |
| 131 | `register_service` | `(name: str, description: str)` | `int (0=success)` | `NOT_SERVICE`, `SERVICE_EXISTS` | Service |
| 132 | `unregister_service` | `(name: str)` | `int (0=success)` | `NOT_SERVICE`, `PERMISSION_DENIED` | Service |
| 133 | `get_services` | `()` | `list (services)` | None | Service |
| 134 | `get_service_handle` | `(name: str)` | `int (handle)` | `SERVICE_NOT_FOUND` | Service |

---

## 3. GUI/TUI Operations

**IMPORTANT**: GUI/TUI syscalls require **output lock** to prevent race conditions between processes.

| ID | Syscall | Parameters | Returns | Errors | Scope | Notes |
|---|---------|-----------|---------|--------|-------|-------|
| 301 | `tui_acquire_output_lock` | `(timeout_ms: int=0)` | `int (0=success)` | `LOCK_TIMEOUT`, `DEADLOCK` | Both | Exclusive write access; blocks if locked |
| 302 | `tui_release_output_lock` | `()` | `int (0=success)` | `NOT_LOCKED`, `PERMISSION_DENIED` | Both | Release output lock |
| 303 | `tui_print` | `(text: str)` | `int (0=success)` | `REQUIRES_LOCK`, `IO_ERROR` | Both | Requires lock; no newline |
| 304 | `tui_println` | `(text: str)` | `int (0=success)` | `REQUIRES_LOCK`, `IO_ERROR` | Both | Requires lock; adds newline |
| 305 | `tui_printf` | `(format: str, args: list)` | `int (0=success)` | `REQUIRES_LOCK`, `FORMAT_ERROR` | Both | Printf-style formatting |
| 306 | `tui_write_string` | `(text: str, x: int, y: int)` | `int (0=success)` | `REQUIRES_LOCK`, `OUT_OF_BOUNDS` | Both | Write at position |
| 307 | `tui_clear_screen` | `()` | `int (0=success)` | `REQUIRES_LOCK`, `IO_ERROR` | Both | Clear entire screen |
| 308 | `tui_clear_line` | `()` | `int (0=success)` | `REQUIRES_LOCK`, `IO_ERROR` | Both | Clear current line |
| 309 | `tui_flush` | `()` | `int (0=success)` | `REQUIRES_LOCK`, `IO_ERROR` | Both | Flush output buffer |
| 310 | `tui_set_cursor_pos` | `(x: int, y: int)` | `int (0=success)` | `REQUIRES_LOCK`, `OUT_OF_BOUNDS` | Both | Move cursor to (x, y) |
| 311 | `tui_get_cursor_pos` | `()` | `dict ({x, y})` | `REQUIRES_LOCK` | Both | Get current cursor position |
| 312 | `tui_move_cursor` | `(dx: int, dy: int)` | `int (0=success)` | `REQUIRES_LOCK`, `OUT_OF_BOUNDS` | Both | Relative cursor movement |
| 313 | `tui_hide_cursor` | `()` | `int (0=success)` | `REQUIRES_LOCK`, `IO_ERROR` | Both | Hide cursor |
| 314 | `tui_show_cursor` | `()` | `int (0=success)` | `REQUIRES_LOCK`, `IO_ERROR` | Both | Show cursor |
| 315 | `tui_set_color` | `(color: int)` | `int (0=success)` | `REQUIRES_LOCK`, `INVALID_COLOR` | Both | Set foreground color |
| 316 | `tui_set_bg_color` | `(color: int)` | `int (0=success)` | `REQUIRES_LOCK`, `INVALID_COLOR` | Both | Set background color |
| 317 | `tui_reset_colors` | `()` | `int (0=success)` | `REQUIRES_LOCK`, `IO_ERROR` | Both | Reset to default colors |
| 318 | `tui_set_bold` | `(enable: int)` | `int (0=success)` | `REQUIRES_LOCK` | Both | Enable/disable bold |
| 319 | `tui_set_underline` | `(enable: int)` | `int (0=success)` | `REQUIRES_LOCK` | Both | Enable/disable underline |
| 320 | `tui_reset_formatting` | `()` | `int (0=success)` | `REQUIRES_LOCK` | Both | Reset all formatting |
| 321 | `tui_read_char` | `()` | `str (char)` | `IO_ERROR` | Both | Blocking read of single char |
| 322 | `tui_read_line` | `()` | `str (line)` | `IO_ERROR`, `EOF` | Both | Blocking read of line |
| 323 | `tui_read_key` | `()` | `int (key_code)` | `IO_ERROR` | Both | Blocking read of key |
| 324 | `tui_get_screen_size` | `()` | `dict ({width, height})` | None | Both | Get TUI dimensions |
| 325 | `tui_refresh` | `()` | `int (0=success)` | `REQUIRES_LOCK`, `IO_ERROR` | Both | Refresh screen |
| 326 | `tui_is_tty` | `()` | `int (1=yes, 0=no)` | None | Both | Check if TTY available |

---

## 4. DLL/Module Loading

| ID | Syscall | Parameters | Returns | Errors | Scope |
|---|---------|-----------|---------|--------|-------|
| 401 | `load_library` | `(path: str)` | `int (handle)` | `FILE_NOT_FOUND`, `INVALID_DLL`, `LOAD_ERROR` | Both |
| 402 | `load_dll` | `(path: str)` | `int (handle)` | `FILE_NOT_FOUND`, `INVALID_DLL`, `LOAD_ERROR` | Both |
| 403 | `unload_library` | `(handle: int)` | `int (0=success)` | `INVALID_HANDLE`, `IN_USE` | Both |
| 404 | `get_module_handle` | `(name: str)` | `int (handle)` | `MODULE_NOT_FOUND` | Both |
| 405 | `reload_module` | `(handle: int)` | `int (0=success)` | `INVALID_HANDLE`, `LOAD_ERROR` | Both |
| 406 | `get_dll_exports` | `(handle: int)` | `list (exports)` | `INVALID_HANDLE` | Both |
| 407 | `get_dll_imports` | `(handle: int)` | `list (imports)` | `INVALID_HANDLE` | Both |
| 408 | `get_dll_info` | `(handle: int)` | `dict (dll_info)` | `INVALID_HANDLE` | Both |
| 409 | `get_dll_version` | `(handle: int)` | `str (version)` | `INVALID_HANDLE` | Both |
| 410 | `get_procedure_address` | `(handle: int, name: str)` | `int (address)` | `INVALID_HANDLE`, `PROCEDURE_NOT_FOUND` | Both |
| 411 | `get_symbol_address` | `(handle: int, symbol: str)` | `int (address)` | `INVALID_HANDLE`, `SYMBOL_NOT_FOUND` | Both |
| 412 | `list_loaded_modules` | `()` | `list (modules)` | None | Both |
| 413 | `link_module` | `(handle1: int, handle2: int)` | `int (0=success)` | `INVALID_HANDLE`, `LINK_ERROR` | Both |
| 414 | `unlink_module` | `(handle1: int, handle2: int)` | `int (0=success)` | `INVALID_HANDLE`, `NOT_LINKED` | Both |
| 415 | `get_module_base` | `(handle: int)` | `int (base_address)` | `INVALID_HANDLE` | Both |

---

## 5. Memory Management

**Note**: No malloc/free syscalls. Python manages memory natively. These syscalls provide monitoring and limits only.

| ID | Syscall | Parameters | Returns | Errors | Scope |
|---|---------|-----------|---------|--------|-------|
| 501 | `get_process_memory_usage` | `(pid: int)` | `dict ({rss, vms, shared})` | `INVALID_PID` | Both |
| 502 | `get_total_memory` | `()` | `int (bytes)` | None | Both |
| 503 | `get_free_memory` | `()` | `int (bytes)` | None | Both |
| 504 | `get_memory_stats` | `()` | `dict (stats)` | None | Both |
| 505 | `set_memory_limit` | `(pid: int, limit_bytes: int)` | `int (0=success)` | `INVALID_PID`, `INVALID_LIMIT` | Both |
| 506 | `get_memory_limit` | `(pid: int)` | `int (limit_bytes)` | `INVALID_PID` | Both |
| 507 | `get_memory_info` | `(pid: int)` | `dict (memory_info)` | `INVALID_PID` | Both |
| 508 | `get_heap_usage` | `(pid: int)` | `int (bytes)` | `INVALID_PID` | Both |

---

## 6. Device I/O & Control

| ID | Syscall | Parameters | Returns | Errors | Scope |
|---|---------|-----------|---------|--------|-------|
| 601 | `open_device` | `(device_name: str)` | `int (device_fd)` | `DEVICE_NOT_FOUND`, `PERMISSION_DENIED` | Both |
| 602 | `close_device` | `(device_fd: int)` | `int (0=success)` | `INVALID_DEVICE`, `IO_ERROR` | Both |
| 603 | `ioctl` | `(fd: int, request: int, args: any)` | `int (result)` | `INVALID_FD`, `IOCTL_ERROR` | Both |
| 604 | `poll` | `(fds: list, timeout_ms: int)` | `list (ready_fds)` | `INVALID_FD`, `TIMEOUT` | Both |
| 605 | `enumerate_devices` | `()` | `list (devices)` | None | Both |
| 606 | `get_device_info` | `(device_name: str)` | `dict (info)` | `DEVICE_NOT_FOUND` | Both |
| 607 | `get_device_status` | `(device_name: str)` | `dict (status)` | `DEVICE_NOT_FOUND` | Both |
| 608 | `read_block` | `(fd: int, block_id: int, size: int)` | `str (data)` | `INVALID_FD`, `IO_ERROR` | Both |
| 609 | `write_block` | `(fd: int, block_id: int, data: str)` | `int (0=success)` | `INVALID_FD`, `IO_ERROR` | Both |
| 610 | `flush_device` | `(fd: int)` | `int (0=success)` | `INVALID_FD`, `IO_ERROR` | Both |
| 611 | `seek_device` | `(fd: int, offset: int, whence: int)` | `int (new_pos)` | `INVALID_FD`, `SEEK_ERROR` | Both |
| 612 | `putchar` | `(char: str)` | `int (0=success)` | `INVALID_CHAR`, `IO_ERROR` | Both |
| 613 | `getchar` | `()` | `str (char)` | `IO_ERROR`, `EOF` | Both |
| 614 | `read_char` | `()` | `str (char)` | `IO_ERROR` | Both |
| 615 | `write_char` | `(char: str)` | `int (0=success)` | `INVALID_CHAR`, `IO_ERROR` | Both |
| 616 | `read_raw` | `(fd: int, size: int)` | `bytes (data)` | `INVALID_FD`, `IO_ERROR` | Both |
| 617 | `write_raw` | `(fd: int, data: bytes)` | `int (bytes_written)` | `INVALID_FD`, `IO_ERROR` | Both |
| 618 | `select` | `(read_fds: list, write_fds: list, timeout_ms: int)` | `dict (ready_fds)` | `INVALID_FD`, `TIMEOUT` | Both |
| 619 | `pselect` | `(read_fds: list, write_fds: list, timeout_ns: int)` | `dict (ready_fds)` | `INVALID_FD`, `TIMEOUT` | Both |
| 620 | `epoll_create` | `()` | `int (epoll_fd)` | `RESOURCE_EXHAUSTED` | Both |
| 621 | `epoll_ctl` | `(epoll_fd: int, op: int, fd: int, events: int)` | `int (0=success)` | `INVALID_FD`, `EPOLL_ERROR` | Both |
| 622 | `epoll_wait` | `(epoll_fd: int, max_events: int, timeout_ms: int)` | `list (events)` | `INVALID_FD`, `TIMEOUT` | Both |

---

## 7. Signals & IPC

| ID | Syscall | Parameters | Returns | Errors | Scope |
|---|---------|-----------|---------|--------|-------|
| 701 | `kill` | `(pid: int, signal: int)` | `int (0=success)` | `INVALID_PID`, `INVALID_SIGNAL` | Both |
| 702 | `raise` | `(signal: int)` | `int (0=success)` | `INVALID_SIGNAL` | Both |
| 703 | `signal` | `(signal_num: int, handler: func)` | `func (old_handler)` | `INVALID_SIGNAL` | Both |
| 704 | `sigaction` | `(signal_num: int, action: dict)` | `dict (old_action)` | `INVALID_SIGNAL` | Both |
| 705 | `sigprocmask` | `(how: int, set: list, oldset: list)` | `int (0=success)` | `INVALID_SIGNAL` | Both |
| 706 | `sigpending` | `()` | `list (pending_signals)` | None | Both |
| 707 | `sigaltstack` | `(stack: dict)` | `int (0=success)` | `STACK_ERROR` | Both |
| 708 | `send_message` | `(pid: int, msg_type: int, data: str)` | `int (0=success)` | `INVALID_PID`, `QUEUE_FULL` | Both |
| 709 | `recv_message` | `(msg_type: int, flags: int)` | `dict (message)` | `QUEUE_EMPTY`, `TIMEOUT` | Both |
| 710 | `msgget` | `(key: int, flags: int)` | `int (queue_id)` | `QUEUE_EXISTS`, `PERMISSION_DENIED` | Both |
| 711 | `msgsnd` | `(queue_id: int, msg: dict, flags: int)` | `int (0=success)` | `INVALID_QUEUE`, `QUEUE_FULL` | Both |
| 712 | `msgrcv` | `(queue_id: int, msg_type: int, flags: int)` | `dict (message)` | `INVALID_QUEUE`, `QUEUE_EMPTY` | Both |
| 713 | `msgctl` | `(queue_id: int, cmd: int, buf: dict)` | `int (0=success)` | `INVALID_QUEUE`, `PERMISSION_DENIED` | Both |
| 714 | `shmget` | `(key: int, size: int, flags: int)` | `int (shmid)` | `SHM_EXISTS`, `PERMISSION_DENIED` | Both |
| 715 | `shmatt` | `(shmid: int, addr: int, flags: int)` | `int (addr)` | `INVALID_SHMID`, `SHM_FULL` | Both |
| 716 | `shmdt` | `(addr: int)` | `int (0=success)` | `INVALID_ADDR`, `NOT_ATTACHED` | Both |
| 717 | `shmctl` | `(shmid: int, cmd: int, buf: dict)` | `int (0=success)` | `INVALID_SHMID`, `PERMISSION_DENIED` | Both |
| 718 | `pipe` | `()` | `list ([read_fd, write_fd])` | `RESOURCE_EXHAUSTED` | Both |
| 719 | `mkfifo` | `(path: str, mode: int)` | `int (0=success)` | `FILE_EXISTS`, `PERMISSION_DENIED` | Both |
| 720 | `cond_destroy` | `(cond_id: int)` | `int (0=success)` | `INVALID_COND`, `IN_USE` | Both |

---

## 8. Threading

| ID | Syscall | Parameters | Returns | Errors | Scope |
|---|---------|-----------|---------|--------|-------|
| 801 | `thread_create` | `(func: func, args: list, priority: int)` | `int (thread_id)` | `RESOURCE_EXHAUSTED`, `INVALID_PRIORITY` | Both |
| 802 | `thread_exit` | `(code: int)` | `void` | None | Both |
| 803 | `thread_join` | `(thread_id: int, timeout_ms: int)` | `int (exit_code)` | `INVALID_THREAD`, `TIMEOUT` | Both |
| 804 | `thread_detach` | `(thread_id: int)` | `int (0=success)` | `INVALID_THREAD`, `ALREADY_DETACHED` | Both |
| 805 | `thread_self` | `()` | `int (thread_id)` | None | Both |
| 806 | `thread_equal` | `(t1: int, t2: int)` | `int (1=equal, 0=not)` | None | Both |
| 807 | `thread_cancel` | `(thread_id: int)` | `int (0=success)` | `INVALID_THREAD`, `ALREADY_CANCELLED` | Both |
| 808 | `thread_setcancelstate` | `(state: int)` | `int (old_state)` | `INVALID_STATE` | Both |
| 809 | `thread_testcancel` | `()` | `int (0=success)` | None | Both |
| 810 | `thread_cleanup_push` | `(func: func, arg: any)` | `int (0=success)` | None | Both |
| 811 | `thread_cleanup_pop` | `(execute: int)` | `int (0=success)` | None | Both |
| 812 | `mutex_create` | `(type: int)` | `int (mutex_id)` | `RESOURCE_EXHAUSTED` | Both |
| 813 | `mutex_lock` | `(mutex_id: int, timeout_ms: int)` | `int (0=success)` | `INVALID_MUTEX`, `DEADLOCK`, `TIMEOUT` | Both |
| 814 | `mutex_unlock` | `(mutex_id: int)` | `int (0=success)` | `INVALID_MUTEX`, `NOT_LOCKED` | Both |
| 815 | `mutex_destroy` | `(mutex_id: int)` | `int (0=success)` | `INVALID_MUTEX`, `IN_USE` | Both |
| 816 | `mutex_trylock` | `(mutex_id: int)` | `int (0=success, 1=busy)` | `INVALID_MUTEX` | Both |
| 817 | `cond_create` | `()` | `int (cond_id)` | `RESOURCE_EXHAUSTED` | Both |
| 818 | `cond_wait` | `(cond_id: int, mutex_id: int, timeout_ms: int)` | `int (0=success)` | `INVALID_COND`, `INVALID_MUTEX`, `TIMEOUT` | Both |
| 819 | `cond_signal` | `(cond_id: int)` | `int (0=success)` | `INVALID_COND` | Both |
| 820 | `cond_broadcast` | `(cond_id: int)` | `int (0=success)` | `INVALID_COND` | Both |

---

## 9. Time Operations

| ID | Syscall | Parameters | Returns | Errors | Scope |
|---|---------|-----------|---------|--------|-------|
| 901 | `time` | `()` | `int (seconds)` | None | Both |
| 902 | `gettimeofday` | `()` | `dict ({sec, usec})` | None | Both |
| 903 | `settimeofday` | `(sec: int, usec: int)` | `int (0=success)` | `PERMISSION_DENIED` | Both |
| 904 | `clock_gettime` | `(clock_id: int)` | `dict ({sec, nsec})` | `INVALID_CLOCK` | Both |
| 905 | `clock_settime` | `(clock_id: int, sec: int, nsec: int)` | `int (0=success)` | `INVALID_CLOCK`, `PERMISSION_DENIED` | Both |
| 906 | `timer_create` | `(clock_id: int, callback: func)` | `int (timer_id)` | `INVALID_CLOCK`, `RESOURCE_EXHAUSTED` | Both |
| 907 | `timer_settime` | `(timer_id: int, initial_ms: int, interval_ms: int)` | `int (0=success)` | `INVALID_TIMER` | Both |
| 908 | `timer_delete` | `(timer_id: int)` | `int (0=success)` | `INVALID_TIMER` | Both |
| 909 | `sleep` | `(seconds: int)` | `int (0=success)` | None | Both |
| 910 | `usleep` | `(microseconds: int)` | `int (0=success)` | None | Both |

---

## 10. Miscellaneous

| ID | Syscall | Parameters | Returns | Errors | Scope |
|---|---------|-----------|---------|--------|-------|
| 1001 | `sysinfo` | `()` | `dict (system_info)` | None | Both |
| 1002 | `uname` | `()` | `dict ({sysname, nodename, release})` | None | Both |
| 1003 | `hostname` | `()` | `str (hostname)` | None | Both |
| 1004 | `get_os_version` | `()` | `str (version)` | None | Both |
| 1005 | `get_cpu_count` | `()` | `int (count)` | None | Both |
| 1006 | `get_uptime` | `()` | `int (seconds)` | None | Both |
| 1007 | `getenv` | `(key: str)` | `str (value)` | `ENV_NOT_FOUND` | Both |
| 1008 | `setenv` | `(key: str, value: str)` | `int (0=success)` | None | Both |
| 1009 | `unsetenv` | `(key: str)` | `int (0=success)` | `ENV_NOT_FOUND` | Both |
| 1010 | `get_all_env` | `()` | `dict (environment)` | None | Both |
| 1011 | `perror` | `(message: str)` | `void` | None | Both |
| 1012 | `strerror` | `(errno: int)` | `str (error_msg)` | None | Both |
| 1013 | `get_last_error` | `()` | `int (errno)` | None | Both |
| 1014 | `debug_print` | `(message: str)` | `int (0=success)` | None | Both |
| 1015 | `trace` | `(enable: int)` | `int (0=success)` | None | Both |
| 1016 | `halt` | `()` | `void` | None | Service |

---

## Error Codes Reference

```
Generic Errors:
- SUCCESS (0)
- INVALID_FD (-1)
- INVALID_PID (-2)
- PERMISSION_DENIED (-3)
- FILE_NOT_FOUND (-4)
- RESOURCE_EXHAUSTED (-5)
- INVALID_ARGUMENT (-6)
- IO_ERROR (-7)
- TIMEOUT (-8)
- NOT_FOUND (-9)

File System:
- FILE_EXISTS (-20)
- IS_DIRECTORY (-21)
- NOT_DIRECTORY (-22)
- PATH_NOT_FOUND (-23)
- DIR_NOT_EMPTY (-24)

Process/Thread:
- INVALID_PRIORITY (-40)
- NO_CHILD_PROCESSES (-41)
- INVALID_STATE (-42)
- DEADLOCK (-43)

Device:
- DEVICE_NOT_FOUND (-60)
- INVALID_DEVICE (-61)

IPC/Signals:
- INVALID_SIGNAL (-80)
- QUEUE_FULL (-81)
- QUEUE_EMPTY (-82)

GUI/TUI:
- REQUIRES_LOCK (-100)
- LOCK_TIMEOUT (-101)
- OUT_OF_BOUNDS (-102)
- INVALID_COLOR (-103)
```

---

## Syscall Categories Summary

| Category | ID Range | Count | Key Feature |
|----------|----------|-------|------------|
| File I/O | 1-22 | 22 | Essential filesystem ops |
| Process Management | 101-134 | 34 | Process + service control |
| GUI/TUI | 301-326 | 26 | Output lock mechanism |
| DLL/Module Loading | 401-415 | 15 | Dynamic library support |
| Memory Management | 501-508 | 8 | Monitoring only (no malloc) |
| Device I/O | 601-622 | 22 | Block/char devices, polling |
| Signals & IPC | 701-720 | 20 | Signals, queues, pipes |
| Threading | 801-820 | 20 | Threads, mutexes, conditions |
| Time Operations | 901-910 | 10 | Timers, clocks, sleep |
| Miscellaneous | 1001-1016 | 16 | System info, debugging |
| **TOTAL** | | **~202** | |

---

## Notes for Developers

**Scope Restrictions**: Syscalls marked "Both" are available to both Programs and Services. "Program" syscalls are available only to user programs. "Service" syscalls are available only to services.

**GUI/TUI Output Lock**: Always acquire the output lock before performing TUI operations to prevent interleaved output from multiple processes. A single process holds exclusive write access until the lock is released. Optional timeout parameter available in acquire operation.

**Memory Management**: No manual allocation functions available. Python manages all memory natively. Provided syscalls are for monitoring process memory usage, setting resource limits, and retrieving memory statistics.

**DLL/Module Loading**: Supports Windows-style dynamic library loading and unloading. Modules can be linked together for complex multi-module applications. Symbol and procedure address resolution available for loaded libraries.

**Error Handling**: All syscalls return status codes or data on success, with negative error codes indicating failure. Use the strerror() syscall to obtain human-readable error messages for debugging.

**Service-Only Syscalls**: Processes attempting to use service-restricted syscalls will receive PERMISSION_DENIED error. Only processes registered as services can use register_service, unregister_service, get_services, and get_service_handle.

**Threading Synchronization**: Mutex and condition variable syscalls support timeouts to prevent deadlock. Threads can be created with priority settings and cancelled with cleanup handler support.

---

**Documentation Version**: 1.0  
**Last Updated**: 2026-04-23  
**Educational OS**: MyPyOS v1.0
