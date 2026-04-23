# Memory Management Syscalls

**Kategorie-ID**: 501-508  
**Scope**: Speicher-Überwachung (kein malloc/free!)

[← Übersicht](README.md) | [← Zurück: DLL Loading](04-DLLModuleLoading.md) | [Nächste: Device I/O →](06-DeviceIO.md)

---

## Wichtig: Keine malloc/free!

Es gibt **KEINE malloc(), free(), realloc() Syscalls**. Python verwaltet Speicher automatisch!

Diese Kategorie bietet nur **Monitoring und Limits**.

| ID | Syscall | Beschreibung |
|---|---------|------------|
| 501 | `get_process_memory_usage` | Speichernutzung abrufen |
| 502 | `get_total_memory` | Gesamtspeicher |
| 503 | `get_free_memory` | Verfügbarer Speicher |
| 504 | `get_memory_stats` | Speicher-Statistiken |
| 505 | `set_memory_limit` | Speicherlimit setzen |
| 506 | `get_memory_limit` | Speicherlimit abrufen |
| 507 | `get_memory_info` | Detaillierte Info |
| 508 | `get_heap_usage` | Heap-Nutzung |

---

## Speicher in MyPyOS

Python-Variablen werden nativ verwaltet:

```python
# Alles läuft automatisch
my_list = [1, 2, 3, 4, 5]  # Speicher wird automatisch allokiert
my_string = "Hello World"   # Speicher wird automatisch allokiert
my_dict = {"key": "value"}  # Speicher wird automatisch allokiert

# Keine manuellen Allokationen nötig - Python macht es!
```

---

## Detaillierte Beschreibungen

### 501. `get_process_memory_usage` - Speichernutzung

**Parameter**: `(pid: int)`  
**Rückgabe**: `dict (stats)`

**Beispiel**:
```python
# Speicher des aktuellen Prozesses
my_pid = syscall(105)  # getpid
mem = syscall(501, my_pid)

print(f"RSS (Resident): {mem['rss']} bytes")
print(f"VMS (Virtual): {mem['vms']} bytes")
print(f"Shared: {mem['shared']} bytes")

# Ausgabe:
# RSS (Resident): 52428800 bytes (50 MB)
# VMS (Virtual): 104857600 bytes (100 MB)
# Shared: 10485760 bytes (10 MB)

# Anderen Prozess überwachen
mem = syscall(501, 1234)
print(f"Prozess 1234 nutzt: {mem['rss']} bytes")
```

---

### 502. `get_total_memory` - Gesamtspeicher

**Parameter**: `()`  
**Rückgabe**: `int (bytes)`

**Beispiel**:
```python
total = syscall(502)
print(f"Gesamtspeicher: {total / (1024**3):.2f} GB")

# Typische Ausgabe:
# Gesamtspeicher: 16.00 GB
```

---

### 503. `get_free_memory` - Freier Speicher

**Parameter**: `()`  
**Rückgabe**: `int (bytes)`

**Beispiel**:
```python
free = syscall(503)
print(f"Freier Speicher: {free / (1024**2):.0f} MB")

# Typische Ausgabe:
# Freier Speicher: 4096 MB
```

---

### 504. `get_memory_stats` - Speicher-Statistiken

**Parameter**: `()`  
**Rückgabe**: `dict (stats)`

**Beispiel**:
```python
stats = syscall(504)

print(f"Total: {stats['total'] / (1024**3):.2f} GB")
print(f"Used: {stats['used'] / (1024**3):.2f} GB")
print(f"Free: {stats['free'] / (1024**3):.2f} GB")
print(f"Available: {stats['available'] / (1024**3):.2f} GB")
print(f"Percent: {stats['percent']:.1f}%")

# Ausgabe:
# Total: 16.00 GB
# Used: 12.00 GB
# Free: 4.00 GB
# Available: 5.00 GB
# Percent: 75.0%
```

---

### 505. `set_memory_limit` - Speicherlimit setzen

**Parameter**: `(pid: int, limit_bytes: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `INVALID_PID`, `INVALID_LIMIT`

Begrenzt Speichernutzung eines Prozesses.

**Beispiel**:
```python
# Prozess auf 512 MB begrenzen
limit_512mb = 512 * 1024 * 1024
result = syscall(505, 1234, limit_512mb)

if result == 0:
    print("Limit gesetzt")
else:
    print(f"Fehler: {result}")

# Den eigenen Prozess begrenzen
my_pid = syscall(105)  # getpid
syscall(505, my_pid, 256 * 1024 * 1024)  # 256 MB
```

---

### 506. `get_memory_limit` - Limit abrufen

**Parameter**: `(pid: int)`  
**Rückgabe**: `int (limit_bytes)`

**Beispiel**:
```python
limit = syscall(506, 1234)
print(f"Limit: {limit / (1024**2):.0f} MB")

# Ausgabe:
# Limit: 512 MB
```

---

### 507. `get_memory_info` - Detaillierte Info

**Parameter**: `(pid: int)`  
**Rückgabe**: `dict (info)`

**Beispiel**:
```python
info = syscall(507, 1234)

print(f"PID: {info['pid']}")
print(f"Name: {info['name']}")
print(f"RSS: {info['rss'] / (1024**2):.2f} MB")
print(f"VMS: {info['vms'] / (1024**2):.2f} MB")
print(f"Limit: {info['limit'] / (1024**2):.2f} MB")
print(f"Usage %: {info['percent']:.1f}%")

# Ausgabe:
# PID: 1234
# Name: Worker
# RSS: 50.00 MB
# VMS: 100.00 MB
# Limit: 512.00 MB
# Usage %: 9.8%
```

---

### 508. `get_heap_usage` - Heap-Nutzung

**Parameter**: `(pid: int)`  
**Rückgabe**: `int (bytes)`

**Beispiel**:
```python
heap = syscall(508, my_pid)
print(f"Heap: {heap / (1024**2):.2f} MB")
```

---

## Praktische Beispiele

### Speicher-Monitor

```python
def monitor_memory(update_interval=1):
    syscall(301)  # tui_acquire_output_lock
    syscall(307)  # tui_clear_screen
    
    # Header
    syscall(315, 3)  # yellow
    syscall(304, "=== Memory Monitor ===")
    syscall(317)  # reset colors
    
    # Statistiken
    total = syscall(502)
    free = syscall(503)
    stats = syscall(504)
    
    syscall(304, f"Total: {total / (1024**3):.2f} GB")
    syscall(304, f"Free: {free / (1024**3):.2f} GB")
    syscall(304, f"Used: {stats['used'] / (1024**3):.2f} GB ({stats['percent']:.1f}%)")
    
    syscall(302)  # tui_release_output_lock
```

### Prozess-Speicher-Alarm

```python
def check_memory_limit(pid, warning_percent=80):
    info = syscall(507, pid)
    
    if info['percent'] > warning_percent:
        syscall(301)  # acquire lock
        syscall(315, 1)  # red
        syscall(305, "WARNING: {0} using {1:.1f}% of limit!",
                [info['name'], info['percent']])
        syscall(317)  # reset
        syscall(302)  # release lock
        
        return False
    
    return True
```

### Speicher-Statistiken

```python
def show_memory_stats():
    stats = syscall(504)
    
    # Prozentuale Visualisierung
    used_percent = stats['percent']
    bar_length = 40
    filled = int(bar_length * used_percent / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    syscall(301)  # acquire lock
    syscall(315, 2)  # green
    syscall(305, "Memory: [{0}] {1:.1f}%",
            [bar, used_percent])
    syscall(317)
    syscall(302)  # release lock
```

---

## Wichtige Konzepte

### RSS vs VMS vs Heap

- **RSS (Resident Set Size)**: Physischer RAM tatsächlich genutzt
- **VMS (Virtual Memory Size)**: Allokierter virtueller Speicher
- **Heap**: Python-Objekt-Heap

### Speicherlimits

- Mit `set_memory_limit()` einen Prozess begrenzen
- Wenn Limit überschritten: Prozess wird terminiert
- Limit für Init-Prozess: System-Default

### Python Memory Management

```python
# Python verwaltet automatisch:
big_list = [i for i in range(1000000)]  # 1 Million Einträge
# Speicher wird automatisch allokiert

del big_list  # Speicher wird automatisch freigegeben
# Garbage Collector kümmert sich darum
```

---

## Verwandte Kategorien

- [← Zurück: DLL Loading](04-DLLModuleLoading.md)
- [Nächste: Device I/O →](06-DeviceIO.md)
- [Process Management](02-ProcessManagement.md)

---

**Kategorie**: Memory Management (IDs 501-508)  
**Letztes Update**: 2026-04-23
