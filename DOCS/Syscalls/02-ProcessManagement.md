# Process Management Syscalls

**Kategorie-ID**: 101-134  
**Scope**: Prozess- und Service-Verwaltung  
**Voraussetzungen**: Keine

[← Übersicht](README.md) | [← Zurück: File I/O](01-FileIO.md) | [Nächste: GUI/TUI →](03-GUITUIOperations.md)

---

## Übersicht

Prozessmanagement-Syscalls für Erstellung, Steuerung, Prioritäten und Ressourcenverwaltung. Service-spezifische Operationen nur für registrierte Services verfügbar.

| ID | Syscall | Beschreibung | Scope |
|---|---------|------------|-------|
| 101 | `create_process` | Neuen Prozess erstellen | Both |
| 102 | `exit` | Prozess beenden | Both |
| 103 | `wait` | Auf Kinder warten | Both |
| 104 | `waitpid` | Auf spezifischen Prozess warten | Both |
| 105 | `getpid` | Aktuelle Prozess-ID abrufen | Both |
| 106 | `getppid` | Eltern-Prozess-ID abrufen | Both |
| 107 | `terminate_process` | Prozess beenden | Both |
| 108 | `kill_process` | Prozess mit Signal beenden | Both |
| 109 | `getuid` | User-ID abrufen | Both |
| 110 | `setuid` | User-ID ändern | Both |
| 111 | `getgid` | Group-ID abrufen | Both |
| 112 | `setgid` | Group-ID ändern | Both |
| 113 | `getgroups` | Gruppen-Memberships | Both |
| 114 | `setgroups` | Gruppen-Memberships ändern | Both |
| 115 | `getpriority` | Prozess-Priorität abrufen | Both |
| 116 | `setpriority` | Priorität ändern | Both |
| 117 | `nice` | Priorität erhöhen/verringern | Both |
| 118 | `yield_cpu` | CPU-Zeit freigeben | Both |
| 119 | `get_process_env` | Prozess-Umgebung lesen | Both |
| 120 | `set_process_env` | Umgebungsvariable setzen | Both |
| 121 | `getenv` | Umgebungsvariable abrufen | Both |
| 122 | `setenv` | Umgebungsvariable setzen | Both |
| 123 | `unsetenv` | Umgebungsvariable löschen | Both |
| 124 | `get_process_state` | Prozess-Zustand auslesen | Both |
| 125 | `getrusage` | Ressourcen-Nutzung | Both |
| 126 | `get_process_info` | Prozess-Informationen | Both |
| 127 | `get_all_pids` | Alle Prozess-IDs | Both |
| 128 | `getprocesses` | Alle Prozesse auflisten | Both |
| 129 | `get_parent_pid` | Eltern-PID eines Prozesses | Both |
| 130 | `is_service` | Ist der Prozess ein Service? | Both |
| 131 | `register_service` | Als Service registrieren | Service |
| 132 | `unregister_service` | Service abmelden | Service |
| 133 | `get_services` | Alle Services auflisten | Service |
| 134 | `get_service_handle` | Service-Handle abrufen | Service |

---

## Detaillierte Syscall-Beschreibungen

### 101. `create_process` - Prozess erstellen

**Parameter**: `(name: str, code: str)`  
**Rückgabe**: `int (pid)`  
**Fehler**: `INVALID_CODE`, `RESOURCE_EXHAUSTED`

Erstellt einen neuen Prozess mit dem übergebenen Python-Code.

**Beispiel**:
```python
# Einfacher Prozess
code = """
for i in range(5):
    print(f"Worker: {i}")
"""

pid = syscall(101, "MyWorker", code)
print(f"Prozess erstellt: PID={pid}")

# Mit Syscall-Aufrufen
worker_code = """
my_pid = syscall(105)  # getpid
parent_pid = syscall(106)  # getppid
print(f"Ich bin {my_pid}, mein Parent ist {parent_pid}")
"""

pid = syscall(101, "InfoPrinter", worker_code)
```

---

### 102. `exit` - Prozess beenden

**Parameter**: `(code: int)`  
**Rückgabe**: `void`  
**Fehler**: None

Beendet den aktuellen Prozess mit Exit-Code.

**Beispiel**:
```python
# Im Prozess-Code:
if error_occurred:
    syscall(102, 1)  # Fehler-Exit
else:
    syscall(102, 0)  # Erfolg
```

---

### 103-104. `wait` / `waitpid` - Auf Prozesse warten

**Parameter wait**: `()`  
**Parameter waitpid**: `(pid: int)`  
**Rückgabe**: `int (pid / status)`  
**Fehler**: `NO_CHILD_PROCESSES`, `INVALID_PID`

Wartet bis Kind-Prozess beendet ist.

**Beispiel**:
```python
# Prozess erstellen
child_pid = syscall(101, "Child", "print('Hello from child')")

# Auf ihn warten
status = syscall(104, child_pid)
print(f"Kind beendet mit Status: {status}")

# Alle Kinder warten
pid = syscall(103)
```

---

### 105-106. `getpid` / `getppid` - Prozess-IDs

**Parameter**: `()`  
**Rückgabe**: `int (pid / ppid)`  
**Fehler**: None

Gibt aktuelle oder Eltern-Prozess-ID zurück.

**Beispiel**:
```python
my_pid = syscall(105)
parent = syscall(106)
print(f"Ich bin {my_pid}, mein Parent ist {parent}")
```

---

### 107-108. `terminate_process` / `kill_process` - Prozess beenden

**Parameter terminate**: `(pid: int)`  
**Parameter kill**: `(pid: int, signal: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `INVALID_PID`, `PERMISSION_DENIED`

Beendet einen anderen Prozess. `kill_process` sendet Signal.

**Beispiel**:
```python
pid = syscall(101, "Worker", "while True: pass")

# Sofort beenden
result = syscall(107, pid)

# Mit Signal (15 = SIGTERM)
result = syscall(108, pid, 15)
```

---

### 109-112. UIDs und GIDs

**Parameter getuid**: `()`  
**Parameter setuid**: `(uid: int)`  
**Parameter getgid**: `()`  
**Parameter setgid**: `(gid: int)`

Benutzer- und Gruppen-ID Operationen.

**Beispiel**:
```python
# Aktuelle IDs abrufen
uid = syscall(109)
gid = syscall(111)
print(f"UID={uid}, GID={gid}")

# Ändern (erfordert Rechte)
result = syscall(110, 1000)  # setuid
result = syscall(112, 1000)  # setgid
```

---

### 113-114. `getgroups` / `setgroups` - Gruppen

**Parameter getgroups**: `()`  
**Parameter setgroups**: `(gids: list)`  
**Rückgabe**: `list` / `int (0=success)`

Verwaltung von Gruppen-Memberships.

**Beispiel**:
```python
# Gruppen auflisten
groups = syscall(113)
print(f"Gruppen: {groups}")

# Neue Gruppen setzen
result = syscall(114, [1000, 1001, 1002])
```

---

### 115-117. Priorität

**Parameter getpriority**: `(pid: int)`  
**Parameter setpriority**: `(pid: int, priority: int)`  
**Parameter nice**: `(increment: int)`  
**Rückgabe**: `int`

Prioritätsmanagement. Höher = wichtiger.

**Beispiel**:
```python
# Aktuelle Priorität abrufen
prio = syscall(115, 1234)
print(f"Priorität: {prio}")

# Priorität setzen (0-255)
syscall(116, 1234, 200)

# Relative Änderung
new_prio = syscall(117, 10)  # 10 Punkte höher
```

---

### 118. `yield_cpu` - CPU freigeben

**Parameter**: `()`  
**Rückgabe**: `int (0=success)`

Gibt CPU-Zeit an andere Prozesse ab.

**Beispiel**:
```python
for i in range(1000):
    process_item(i)
    if i % 100 == 0:
        syscall(118)  # CPU für andere freigeben
```

---

### 119-123. Umgebungsvariablen

**Parameter get_process_env**: `(pid: int)`  
**Parameter set_process_env**: `(pid: int, key: str, value: str)`  
**Parameter getenv**: `(key: str)`  
**Parameter setenv**: `(key: str, value: str)`  
**Parameter unsetenv**: `(key: str)`

Umgebungs-Management.

**Beispiel**:
```python
# Globale Umgebungsvariable
syscall(122, "MY_VAR", "hello")
value = syscall(121, "MY_VAR")
print(f"MY_VAR={value}")

# Löschen
syscall(123, "MY_VAR")

# Prozess-spezifisch
syscall(120, 1234, "DEBUG", "1")
env = syscall(119, 1234)
print(f"Umgebung: {env}")
```

---

### 124-126. Prozess-Informationen

**Parameter get_process_state**: `(pid: int)`  
**Parameter getrusage**: `(pid: int)`  
**Parameter get_process_info**: `(pid: int)`  
**Rückgabe**: `str` / `dict`

Status und Ressourcennutzung.

**Beispiel**:
```python
# Zustand abrufen (ready, running, waiting, terminated)
state = syscall(124, 1234)
print(f"Prozess-Zustand: {state}")

# Ressourcennutzung
usage = syscall(125, 1234)
print(f"CPU-Zeit: {usage['cpu_time']}")
print(f"Speicher: {usage['memory']}")

# Vollständige Info
info = syscall(126, 1234)
print(f"Name: {info['name']}")
print(f"Status: {info['status']}")
```

---

### 127-128. Alle Prozesse auflisten

**Parameter get_all_pids**: `()`  
**Parameter getprocesses**: `()`  
**Rückgabe**: `list (pids)` / `list (processes)`

Übersicht aller Prozesse.

**Beispiel**:
```python
# Alle PIDs
all_pids = syscall(127)
print(f"Prozesse: {all_pids}")

# Detaillierte Liste
processes = syscall(128)
for proc in processes:
    print(f"{proc['pid']}: {proc['name']} ({proc['state']})")
```

---

### 129. `get_parent_pid` - Eltern-PID

**Parameter**: `(pid: int)`  
**Rückgabe**: `int (ppid)`  
**Fehler**: `INVALID_PID`

**Beispiel**:
```python
ppid = syscall(129, 1234)
print(f"Eltern-Prozess: {ppid}")
```

---

### 130-134. Service Management

**Parameter is_service**: `()`  
**Parameter register_service**: `(name: str, description: str)`  
**Parameter unregister_service**: `(name: str)`  
**Parameter get_services**: `()`  
**Parameter get_service_handle**: `(name: str)`  
**Rückgabe**: `int` / `list` / `int`

Services sind spezielle Prozesse mit erweiterten Rechten.

**Beispiel**:
```python
# Im Service-Prozess:
is_svc = syscall(130)
if is_svc:
    print("Ich bin ein Service")
    
    # Als Service registrieren
    result = syscall(131, "MyService", "Important Background Service")
    
    # Services auflisten
    services = syscall(133)
    print(f"Services: {services}")
    
    # Service-Handle abrufen
    handle = syscall(134, "MyService")
    
    # Service abmelden
    syscall(132, "MyService")
```

---

## Häufige Muster

### Kind-Prozesse warten

```python
# Mehrere Kinder erstellen und warten
pids = []
for i in range(3):
    code = f"print('Worker {i}')"
    pid = syscall(101, f"Worker{i}", code)
    pids.append(pid)

# Auf alle warten
for pid in pids:
    syscall(104, pid)
print("Alle Worker beendet")
```

### Prozess-Monitor

```python
def monitor_process(target_pid):
    while True:
        state = syscall(124, target_pid)
        if state == "terminated":
            break
        
        info = syscall(126, target_pid)
        print(f"{info['name']}: {info['status']}")
        syscall(909, 1)  # 1 Sekunde schlafen

monitor_process(1234)
```

### Service-Handler

```python
def setup_service():
    # Service registrieren
    syscall(131, "WebServer", "HTTP Server Service")
    
    # Alle Services anzeigen
    services = syscall(133)
    
    for service in services:
        print(f"Service: {service['name']}")
        print(f"  Beschreibung: {service['description']}")
        print(f"  Status: {service['status']}")
```

---

## Verwandte Kategorien

- [← Zurück: File I/O](01-FileIO.md)
- [Nächste: GUI/TUI →](03-GUITUIOperations.md)
- [Threading](08-Threading.md)
- [Signals & IPC](07-SignalsIPC.md)

---

**Kategorie**: Process Management (IDs 101-134)  
**Letztes Update**: 2026-04-23
