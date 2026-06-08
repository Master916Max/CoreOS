# Device I/O & Control Syscalls

**Kategorie-ID**: 601-622  
**Scope**: Geräte, Block/Char I/O, Event-basiertes I/O

[← Übersicht](README.md) | [← Zurück: Memory](05-MemoryManagement.md) | [Nächste: Signals/IPC →](07-SignalsIPC.md)

---

## Übersicht

Geräte-Operationen: Block-Devices (Datenträger), Character-Devices (Terminal), Event-basiertes I/O (epoll).

| ID | Syscall | Beschreibung |
|---|---------|------------|
| 601 | `open_device` | Gerät öffnen |
| 602 | `close_device` | Gerät schließen |
| 603 | `ioctl` | Geräte-Steuerung |
| 604 | `poll` | Auf Events warten |
| 605 | `enumerate_devices` | Geräte auflisten |
| 606 | `get_device_info` | Geräte-Informationen |
| 607 | `get_device_status` | Geräte-Status |
| 608 | `read_block` | Block lesen |
| 609 | `write_block` | Block schreiben |
| 610 | `flush_device` | Puffer schreiben |
| 611 | `seek_device` | Position ändern |
| 612 | `putchar` | Zeichen ausgeben |
| 613 | `getchar` | Zeichen einlesen |
| 614 | `read_char` | Zeichen lesen (blockierend) |
| 615 | `write_char` | Zeichen schreiben |
| 616 | `read_raw` | Rohdaten lesen |
| 617 | `write_raw` | Rohdaten schreiben |
| 618 | `select` | Warten auf mehrere FDs |
| 619 | `pselect` | Select mit Präzision |
| 620 | `epoll_create` | Event-Poll erstellen |
| 621 | `epoll_ctl` | Event-Poll konfigurieren |
| 622 | `epoll_wait` | Auf Events warten |

---

## Geräte-Management (601-607)

### 601. `open_device` - Gerät öffnen

**Parameter**: `(device_name: str)`  
**Rückgabe**: `int (device_fd)`

**Beispiel**:
```python
# Terminal öffnen
fd = syscall(601, "/dev/tty")

# Speichermedium
fd = syscall(601, "/dev/hda")

# Null-Device
fd = syscall(601, "/dev/null")
```

---

### 602-607. Geräte-Info & Kontrolle

**Beispiel**:
```python
# Alle Geräte auflisten
devices = syscall(605)
for dev in devices:
    print(f"{dev['name']}: {dev['type']}")

# Info zu Gerät
info = syscall(606, "/dev/hda")
print(f"Größe: {info['size']}")

# Status
status = syscall(607, "/dev/tty")
print(f"Status: {status['ready']}")
```

---

## Block-Device I/O (608-611)

### 608-611. Block-Operationen

**Beispiel**:
```python
fd = syscall(601, "/dev/hda")

# Block 0 lesen (4KB)
data = syscall(608, fd, 0, 4096)

# Block 1 schreiben
syscall(609, fd, 1, "new data...")

# Puffer schreiben
syscall(610, fd)

# Position setzen
syscall(611, fd, 1000, 0)  # 1000 Bytes vom Anfang
```

---

## Character I/O (612-617)

### 612-615. Zeichen-Operationen

**Beispiel**:
```python
# Zeichen ausgeben
syscall(612, 'A')

# Zeichen lesen
char = syscall(613)
char = syscall(614)  # blockierend

# Zeichen schreiben
syscall(615, 'X')
```

---

### 616-617. Rohdaten

**Beispiel**:
```python
fd = syscall(601, "/dev/random")

# 100 Bytes Zufallsdaten lesen
raw_data = syscall(616, fd, 100)

# Rohdaten schreiben
syscall(617, fd, b"binary data")
```

---

## Event-basiertes I/O (618-622)

### 618-619. Select/Pselect

**Beispiel**:
```python
# read_fds, write_fds, timeout_ms
result = syscall(618, [1, 2, 3], [4, 5], 1000)
# Gibt Deskriptoren zurück die bereit sind

# Mit Nanosekunden-Genauigkeit
result = syscall(619, [10], [], 500000000)  # 500ms
```

---

### 620-622. Epoll (effizientes Event-Polling)

**Beispiel**:
```python
# Epoll erstellen
ep_fd = syscall(620)

# FD hinzufügen (Lesen überwachen)
syscall(621, ep_fd, 1, 10, 1)  # op=ADD, fd=10, events=READ

# Auf Events warten
events = syscall(622, ep_fd, 10, 1000)  # max 10 events, 1s timeout

for ev in events:
    print(f"FD {ev['fd']}: events={ev['events']}")
```

---

## Häufige Muster

### Einfaches Device I/O

```python
def read_device(device, size):
    fd = syscall(601, device)
    if fd < 0:
        return None
    
    data = syscall(616, fd, size)
    syscall(602, fd)
    return data
```

### Geräte-Monitor

```python
def monitor_devices():
    devices = syscall(605)
    
    for dev in devices:
        fd = syscall(601, dev['name'])
        if fd > 0:
            status = syscall(607, dev['name'])
            syscall(304, f"{dev['name']}: {status['status']}")
            syscall(602, fd)
```

### Epoll-Event-Loop

```python
def event_loop(fds):
    ep_fd = syscall(620)
    
    for fd in fds:
        syscall(621, ep_fd, 1, fd, 1)  # ADD, READ
    
    while True:
        events = syscall(622, ep_fd, 10, 5000)
        
        for ev in events:
            handle_event(ev['fd'], ev['events'])
```

---

## Verwandte Kategorien

- [← Zurück: Memory Management](05-MemoryManagement.md)
- [Nächste: Signals/IPC →](07-SignalsIPC.md)
- [File I/O](01-FileIO.md)

---

**Kategorie**: Device I/O & Control (IDs 601-622)  
**Letztes Update**: 2026-04-23
