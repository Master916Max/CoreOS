# Signals & IPC Syscalls

**Kategorie-ID**: 701-720  
**Scope**: Signals, Message Queues, Shared Memory, Pipes

[← Übersicht](README.md) | [← Zurück: Device I/O](06-DeviceIO.md) | [Nächste: Threading →](08-Threading.md)

---

## Übersicht

Inter-Process Communication (IPC) und Signal-Handling.

| ID | Syscall | Beschreibung |
|---|---------|------------|
| 701 | `kill` | Signal an Prozess |
| 702 | `raise` | Signal für sich selbst |
| 703 | `signal` | Signal-Handler setzen |
| 704 | `sigaction` | Signal-Aktion konfigurieren |
| 705 | `sigprocmask` | Signal-Maske setzen |
| 706 | `sigpending` | Ausstehende Signals |
| 707 | `sigaltstack` | Alternativer Stack |
| 708 | `send_message` | Nachricht an Prozess |
| 709 | `recv_message` | Nachricht empfangen |
| 710 | `msgget` | Message Queue erstellen |
| 711 | `msgsnd` | In Queue schreiben |
| 712 | `msgrcv` | Aus Queue lesen |
| 713 | `msgctl` | Queue-Kontrolle |
| 714 | `shmget` | Shared Memory erstellen |
| 715 | `shmatt` | Memory attachen |
| 716 | `shmdt` | Memory detachen |
| 717 | `shmctl` | Shared Memory kontrollieren |
| 718 | `pipe` | Pipe erstellen |
| 719 | `mkfifo` | Named Pipe erstellen |
| 720 | `cond_destroy` | Condition freigeben |

---

## Signals (701-707)

### 701-702. Kill / Raise

**Beispiel**:
```python
# Signal an anderen Prozess (15 = SIGTERM)
result = syscall(701, 1234, 15)

# Signal für sich selbst
syscall(702, 9)  # SIGKILL
```

---

### 703-704. Signal-Handler

**Beispiel**:
```python
# Einfacher Handler
def my_handler(sig):
    print(f"Signal {sig} empfangen")

syscall(703, 15, my_handler)  # SIGTERM

# Mit sigaction (erweitert)
action = {
    'handler': my_handler,
    'flags': 0,
    'mask': []
}
syscall(704, 15, action)
```

---

### 705-707. Signal-Maske

**Beispiel**:
```python
# Signal blockieren
syscall(705, 1, [15, 9])  # block SIGTERM, SIGKILL

# Ausstehende Signals
pending = syscall(706)
print(f"Signals: {pending}")

# Alternativer Stack
stack = {'size': 4096, 'address': 0x1000}
syscall(707, stack)
```

---

## Message Queues (708-713)

### 708-709. Einfache Nachrichten

**Beispiel**:
```python
# Nachricht senden
result = syscall(708, 1234, 1, "Hello Process")

# Nachricht empfangen (blockierend)
msg = syscall(709, 1, 0)
print(f"Von {msg['from_pid']}: {msg['data']}")
```

---

### 710-713. Message Queues

**Beispiel**:
```python
# Queue erstellen
queue_id = syscall(710, 12345, 0)

# Nachricht senden
msg = {'type': 1, 'data': 'test'}
syscall(711, queue_id, msg, 0)

# Nachricht empfangen
msg = syscall(712, queue_id, 1, 0)
print(f"Message: {msg}")

# Queue kontrollieren/löschen
syscall(713, queue_id, 2, None)  # cmd=2 (IPC_RMID)
```

---

## Shared Memory (714-717)

### 714-717. Shared Memory Management

**Beispiel**:
```python
# Shared Memory erstellen (1MB)
shmid = syscall(714, 54321, 1024*1024, 0)

# Attachen
addr = syscall(715, shmid, 0, 0)

# Schreiben
# (In echter Implementierung würde man hier Speicher manipulieren)

# Detachen
syscall(716, addr)

# Löschen
syscall(717, shmid, 2, None)  # IPC_RMID
```

---

## Pipes (718-719)

### 718. Pipe

**Beispiel**:
```python
# Pipe erstellen
pipe_fds = syscall(718)
read_fd = pipe_fds[0]
write_fd = pipe_fds[1]

# Daten schreiben
syscall(4, write_fd, "Piped data")

# Daten lesen
data = syscall(3, read_fd, 1024)
print(f"Gelesen: {data}")

# Schließen
syscall(2, read_fd)
syscall(2, write_fd)
```

---

### 719. Named Pipe (FIFO)

**Beispiel**:
```python
# Named Pipe erstellen
result = syscall(719, "C:\\pipes\\mypipe", 0o666)

# Öffnen und nutzen wie normale Datei
fd = syscall(1, "C:\\pipes\\mypipe", "r")
data = syscall(3, fd, 1024)
syscall(2, fd)
```

---

## Häufige Muster

### Signal-Safe Kommunikation

```python
def safe_signal_handler(sig):
    # Signal empfangen
    syscall(301)  # acquire lock
    syscall(304, f"Signal {sig} empfangen!")
    syscall(302)  # release lock

# Handler setzen
syscall(703, 15, safe_signal_handler)
```

### Producer-Consumer mit Pipe

```python
def producer(write_fd):
    for i in range(10):
        data = f"Item {i}\n"
        syscall(4, write_fd, data)
    syscall(2, write_fd)

def consumer(read_fd):
    while True:
        data = syscall(3, read_fd, 1024)
        if not data:
            break
        print(data)
    syscall(2, read_fd)

# Beispiel
fds = syscall(718)  # pipe
# producer(fds[1])
# consumer(fds[0])
```

### Message Queue Server

```python
def message_server():
    queue_id = syscall(710, 99999, 0o666)
    
    while True:
        # Nachricht empfangen
        msg = syscall(712, queue_id, 0, 0)  # type=0 (any)
        
        from_pid = msg['from_pid']
        data = msg['data']
        
        # Antwort senden
        reply = f"Processed: {data}"
        syscall(708, from_pid, 1, reply)
```

---

## Verwandte Kategorien

- [← Zurück: Device I/O](06-DeviceIO.md)
- [Nächste: Threading →](08-Threading.md)
- [Process Management](02-ProcessManagement.md)

---

**Kategorie**: Signals & IPC (IDs 701-720)  
**Letztes Update**: 2026-04-23
