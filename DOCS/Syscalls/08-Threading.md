# Threading Syscalls

**Kategorie-ID**: 801-820  
**Scope**: Threads, Mutexe, Condition Variables

[← Übersicht](README.md) | [← Zurück: Signals/IPC](07-SignalsIPC.md) | [Nächste: Time Operations →](09-TimeOperations.md)

---

## Übersicht

Multi-Threading-Support mit Synchronisationsprimitiven.

| ID | Syscall | Beschreibung |
|---|---------|------------|
| 801 | `thread_create` | Thread erstellen |
| 802 | `thread_exit` | Thread beenden |
| 803 | `thread_join` | Auf Thread warten |
| 804 | `thread_detach` | Thread trennen |
| 805 | `thread_self` | Aktuelle Thread-ID |
| 806 | `thread_equal` | Thread-Vergleich |
| 807 | `thread_cancel` | Thread abbrechen |
| 808 | `thread_setcancelstate` | Cancel-State setzen |
| 809 | `thread_testcancel` | Auf Cancel prüfen |
| 810 | `thread_cleanup_push` | Cleanup-Handler |
| 811 | `thread_cleanup_pop` | Cleanup freigeben |
| 812 | `mutex_create` | Mutex erstellen |
| 813 | `mutex_lock` | Mutex sperren |
| 814 | `mutex_unlock` | Mutex freigeben |
| 815 | `mutex_destroy` | Mutex löschen |
| 816 | `mutex_trylock` | Nicht-blockierendes Sperren |
| 817 | `cond_create` | Condition Variable erstellen |
| 818 | `cond_wait` | Auf Condition warten |
| 819 | `cond_signal` | Condition signalisieren |
| 820 | `cond_broadcast` | Alle Threads wecken |

---

## Thread Management (801-811)

### 801. `thread_create` - Thread erstellen

**Parameter**: `(func: func, args: list, priority: int)`  
**Rückgabe**: `int (thread_id)`

**Beispiel**:
```python
def worker_func(name, count):
    for i in range(count):
        print(f"{name}: {i}")

# Thread erstellen (Priorität 0-255, höher = wichtiger)
tid = syscall(801, worker_func, ["Worker1", 5], 128)
print(f"Thread erstellt: {tid}")
```

---

### 802-804. Thread Steuerung

**Beispiel**:
```python
# Thread-ID abrufen
my_tid = syscall(805)

# Auf Thread warten
result = syscall(803, tid, 5000)  # Timeout 5s

# Thread trennen (kein join möglich)
syscall(804, tid)

# Thread beenden
syscall(802, 0)  # exit code
```

---

### 806-809. Thread-Verwaltung

**Beispiel**:
```python
# Thread-Vergleich
if syscall(806, tid1, tid2):
    print("Gleicher Thread")

# Thread abbrechen
syscall(807, tid)

# Cancel erlauben/verbieten
state = syscall(808, 1)  # 1=enable, 0=disable

# Auf Cancel-Punkt prüfen
syscall(809)
```

---

### 810-811. Cleanup-Handler

**Beispiel**:
```python
def cleanup_func():
    print("Aufräumen...")

# Handler registrieren
syscall(810, cleanup_func, None)

# Später: Handler ausführen
syscall(811, 1)  # 1=execute
```

---

## Mutexe (812-816)

### 812-815. Mutex Grundlagen

**Beispiel**:
```python
# Mutex erstellen (type: 0=normal, 1=recursive)
mutex = syscall(812, 0)

# Sperren (mit Timeout)
result = syscall(813, mutex, 0)  # 0=unbegrenzt
if result == 0:
    # Kritischer Abschnitt
    shared_var = 42
    syscall(814, mutex)  # unlock
else:
    print("Lock fehlgeschlagen!")

# Mutex löschen
syscall(815, mutex)
```

---

### 816. `mutex_trylock` - Nicht-blockierend

**Beispiel**:
```python
result = syscall(816, mutex)
if result == 0:
    print("Lock erfolgreich")
    # ... arbeiten ...
    syscall(814, mutex)
else:
    print("Konnte nicht sperren")
```

---

## Condition Variables (817-820)

### 817-820. Condition Management

**Beispiel**:
```python
# Condition erstellen
cond = syscall(817)
mutex = syscall(812, 0)

# Warten
syscall(301)  # acquire output lock
syscall(304, "Warte auf Signal...")
syscall(302)  # release

result = syscall(818, cond, mutex, 5000)  # Timeout 5s

# Signalisieren (einen Thread wecken)
syscall(819, cond)

# Broadcast (alle Threads wecken)
syscall(820, cond)
```

---

## Häufige Muster

### Geschützte Variable

```python
class SharedVar:
    def __init__(self, value):
        self.value = value
        self.mutex = syscall(812, 0)  # mutex_create
    
    def get(self):
        syscall(813, self.mutex, 0)  # lock
        val = self.value
        syscall(814, self.mutex)       # unlock
        return val
    
    def set(self, val):
        syscall(813, self.mutex, 0)  # lock
        self.value = val
        syscall(814, self.mutex)       # unlock

# Anwendung
shared = SharedVar(0)
new_val = shared.get()
shared.set(42)
```

### Producer-Consumer mit Condition

```python
queue = []
mutex = syscall(812, 0)
cond_empty = syscall(817)
cond_full = syscall(817)

def producer():
    for i in range(10):
        syscall(813, mutex, 0)  # lock
        queue.append(i)
        syscall(819, cond_full)  # signal
        syscall(814, mutex)      # unlock

def consumer():
    while len(queue) > 0:
        syscall(813, mutex, 0)  # lock
        if queue:
            item = queue.pop(0)
            syscall(820, cond_empty)  # broadcast
            syscall(814, mutex)       # unlock
            print(f"Konsumiert: {item}")
        else:
            syscall(818, cond_full, mutex, 1000)  # wait
```

### Thread Pool

```python
def thread_pool_worker(task_queue, mutex):
    while True:
        syscall(813, mutex, 0)  # lock
        if task_queue:
            task = task_queue.pop(0)
            syscall(814, mutex)  # unlock
            
            task()
        else:
            syscall(814, mutex)  # unlock
            syscall(909, 0)      # sleep 0ms
```

---

## Verwandte Kategorien

- [← Zurück: Signals/IPC](07-SignalsIPC.md)
- [Nächste: Time Operations →](09-TimeOperations.md)
- [Process Management](02-ProcessManagement.md)

---

**Kategorie**: Threading (IDs 801-820)  
**Letztes Update**: 2026-04-23
