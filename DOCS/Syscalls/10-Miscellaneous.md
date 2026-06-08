# Miscellaneous Syscalls

**Kategorie-ID**: 1001-1016  
**Scope**: Systeminformationen, Debugging, Fehlerbehandlung

[← Übersicht](README.md) | [← Zurück: Time Operations](09-TimeOperations.md)

---

## Übersicht

Verschiedenes: Systeminformationen, Umgebungsvariablen, Fehlerbehandlung und Debugging.

| ID | Syscall | Beschreibung |
|---|---------|------------|
| 1001 | `sysinfo` | System-Informationen |
| 1002 | `uname` | OS-Informationen |
| 1003 | `hostname` | Rechner-Name |
| 1004 | `get_os_version` | OS-Version |
| 1005 | `get_cpu_count` | Prozessor-Anzahl |
| 1006 | `get_uptime` | System-Uptime |
| 1007 | `getenv` | Umgebungsvariable abrufen |
| 1008 | `setenv` | Umgebungsvariable setzen |
| 1009 | `unsetenv` | Umgebungsvariable löschen |
| 1010 | `get_all_env` | Alle Umgebungsvariablen |
| 1011 | `perror` | Fehler ausgeben |
| 1012 | `strerror` | Fehlertext abrufen |
| 1013 | `get_last_error` | Letzter Fehlercode |
| 1014 | `debug_print` | Debug-Ausgabe |
| 1015 | `trace` | Tracing an/aus |
| 1016 | `halt` | System anhalten |

---

## System-Informationen (1001-1006)

### 1001. `sysinfo` - System-Info

**Parameter**: `()`  
**Rückgabe**: `dict (info)`

**Beispiel**:
```python
info = syscall(1001)
print(f"Uptime: {info['uptime']} Sekunden")
print(f"RAM: {info['total_ram']} bytes")
print(f"Free: {info['free_ram']} bytes")
print(f"Prozesse: {info['process_count']}")
```

---

### 1002. `uname` - OS-Info

**Parameter**: `()`  
**Rückgabe**: `dict (info)`

**Beispiel**:
```python
info = syscall(1002)
print(f"OS: {info['sysname']}")
print(f"Host: {info['nodename']}")
print(f"Version: {info['release']}")
print(f"Arch: {info['machine']}")
```

---

### 1003-1006. Weitere Infos

**Beispiel**:
```python
# Hostname
hostname = syscall(1003)
print(f"Hostname: {hostname}")

# OS-Version
version = syscall(1004)
print(f"Version: {version}")

# CPU-Anzahl
cpus = syscall(1005)
print(f"CPUs: {cpus}")

# Uptime
uptime = syscall(1006)
print(f"Uptime: {uptime}s ({uptime // 3600}h)")
```

---

## Umgebungsvariablen (1007-1010)

### 1007-1009. Umgebungs-Management

**Beispiel**:
```python
# Variable abrufen
value = syscall(1007, "PATH")
print(f"PATH: {value}")

# Variable setzen
syscall(1008, "MY_VAR", "hello world")

# Variable löschen
syscall(1009, "MY_VAR")

# Alle abrufen
all_env = syscall(1010)
for key, value in all_env.items():
    print(f"{key}={value}")
```

---

## Fehlerbehandlung (1011-1013)

### 1011-1013. Error Handling

**Beispiel**:
```python
# Letzte Fehler-ID
last_err = syscall(1013)
print(f"Fehler: {last_err}")

# Fehlertext abrufen
error_msg = syscall(1012, -1)
print(f"Bedeutung: {error_msg}")

# Fehler ausgeben
syscall(1011, "Something failed")
```

---

## Debugging (1014-1015)

### 1014-1015. Debug-Funktionen

**Beispiel**:
```python
# Debug-Ausgabe
syscall(1014, "Checkpoint 1 reached")
syscall(1014, f"Variable x = {x}")

# Tracing ein
syscall(1015, 1)
# ... Operationen werden getraced ...
# Tracing aus
syscall(1015, 0)
```

---

## System-Kontrolle (1016)

### 1016. `halt` - System beenden

**Parameter**: `()`  
**Rückgabe**: `void`  
**Scope**: Service only

**Beispiel**:
```python
# System anhalten (erfordert Service-Rechte)
syscall(1016)
```

---

## Häufige Muster

### System-Status-Report

```python
def system_report():
    syscall(301)  # acquire lock
    
    syscall(304, "=== System Report ===")
    
    info = syscall(1001)
    syscall(304, f"Uptime: {info['uptime'] // 3600}h")
    syscall(304, f"RAM: {info['free_ram'] / (1024**3):.2f} GB free")
    
    uname = syscall(1002)
    syscall(304, f"OS: {uname['sysname']} {uname['release']}")
    
    cpus = syscall(1005)
    syscall(304, f"CPUs: {cpus}")
    
    syscall(302)  # release lock
```

### Umgebungs-Setup

```python
def setup_environment():
    # PATH setzen
    path = syscall(1007, "PATH")
    new_path = path + ";C:\\new\\path"
    syscall(1008, "PATH", new_path)
    
    # Custom Variablen
    syscall(1008, "APP_HOME", "C:\\myapp")
    syscall(1008, "DEBUG", "1")
    
    # Alle anzeigen
    all_env = syscall(1010)
    syscall(1014, f"Environment: {len(all_env)} variables")
```

### Error-Safe Wrapper

```python
def safe_call(func, args):
    try:
        result = func(*args)
        return result, None
    except Exception as e:
        error_msg = syscall(1012, -1)
        syscall(1014, f"Error: {error_msg}")
        return None, error_msg
```

### Debug-Mode Handler

```python
debug_enabled = False

def debug_log(message):
    if debug_enabled:
        timestamp = syscall(902)
        msg = f"[{timestamp['sec']}.{timestamp['usec']}] {message}"
        syscall(1014, msg)

# Anwendung
debug_enabled = syscall(1007, "DEBUG") == "1"
debug_log("Starte Anwendung")
```

---

## Verwandte Kategorien

- [← Zurück: Time Operations](09-TimeOperations.md)
- [Übersicht](README.md)
- [File I/O](01-FileIO.md)
- [Process Management](02-ProcessManagement.md)

---

**Kategorie**: Miscellaneous (IDs 1001-1016)  
**Letztes Update**: 2026-04-23
