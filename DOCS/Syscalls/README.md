# MyPyOS Syscall Reference Documentation

**Version**: 1.0  
**Total Syscalls**: ~202  
**Target OS**: Educational Python-based OS  
**Documentation**: Windows Syntax & Code Examples

---

## Übersicht der Syscall-Kategorien

Hier finden Sie vollständige Dokumentation für alle Syscalls, organisiert nach Kategorie mit detaillierten Beschreibungen und Codebeispielen.

### Kategorie-Verzeichnis

1. **[File I/O & Filesystem](01-FileIO.md)** (22 Syscalls)
   - Essential Dateisystem-Operationen
   - Datei- und Verzeichnisverwaltung
   - Berechtigungen und Metadaten

2. **[Process Management](02-ProcessManagement.md)** (32 Syscalls)
   - Prozesserstellung und -verwaltung
   - Service-Operationen
   - Prioritäten und Ressourcen

3. **[GUI/TUI Operations](03-GUITUIOperations.md)** (25 Syscalls)
   - Terminal-Ausgabe mit Output-Lock
   - Cursor- und Farbkontrolle
   - Benutzer-Eingabe

4. **[DLL/Module Loading](04-DLLModuleLoading.md)** (15 Syscalls)
   - Dynamisches Laden von Bibliotheken
   - Symbol- und Prozedur-Auflösung
   - Modulverwaltung

5. **[Memory Management](05-MemoryManagement.md)** (8 Syscalls)
   - Speicher-Überwachung
   - Speicherlimits
   - Heap-Informationen

6. **[Device I/O & Control](06-DeviceIO.md)** (22 Syscalls)
   - Geräte-Operationen
   - Block- und Character-Geräte
   - Event-basiertes I/O

7. **[Signals & IPC](07-SignalsIPC.md)** (20 Syscalls)
   - Signal-Verwaltung
   - Message Queues
   - Shared Memory
   - Pipes

8. **[Threading](08-Threading.md)** (20 Syscalls)
   - Thread-Erstellung und -Verwaltung
   - Mutex und Synchronisation
   - Condition Variables

9. **[Time Operations](09-TimeOperations.md)** (10 Syscalls)
   - Zeit- und Uhr-Funktionen
   - Timer und Verzögerungen
   - Timing-Informationen

10. **[Miscellaneous](10-Miscellaneous.md)** (16 Syscalls)
    - Systeminformationen
    - Umgebungsvariablen
    - Fehlerbehandlung

---

## Schnelleinstieg

### Typisches Codebeispiel

```python
# Syscalls im MyPyOS aufrufen
# Die SyscallManager-Instanz steht über das Process-Objekt zur Verfügung

# Beispiel 1: Datei öffnen und lesen
pid = syscall(105)  # getpid()
fd = syscall(1, "test.txt", "r")  # open()
content = syscall(3, fd, 1024)  # read()
syscall(2, fd)  # close()

# Beispiel 2: TUI mit Output-Lock
syscall(301)  # tui_acquire_output_lock()
syscall(304, "Hello World")  # tui_println()
syscall(302)  # tui_release_output_lock()

# Beispiel 3: Prozess erstellen
new_pid = syscall(101, "Worker", "print('test')")  # create_process()
syscall(104, new_pid)  # waitpid()
```

---

## Syscall-Nummern-Referenz

| Bereich | Kategorie | IDs |
|---------|-----------|-----|
| **Datei I/O** | File I/O & Filesystem | 1-22 |
| **Prozesse** | Process Management | 101-134 |
| **GUI/TUI** | GUI/TUI Operations | 301-326 |
| **Module** | DLL/Module Loading | 401-415 |
| **Speicher** | Memory Management | 501-508 |
| **Geräte** | Device I/O & Control | 601-622 |
| **IPC** | Signals & IPC | 701-720 |
| **Threads** | Threading | 801-820 |
| **Zeit** | Time Operations | 901-910 |
| **Sonstiges** | Miscellaneous | 1001-1016 |

---

## Error Codes

Alle Syscalls geben im Fehlerfall negative Fehlercodes zurück:

### Generische Fehler
```
0    SUCCESS
-1   INVALID_FD
-2   INVALID_PID
-3   PERMISSION_DENIED
-4   FILE_NOT_FOUND
-5   RESOURCE_EXHAUSTED
-6   INVALID_ARGUMENT
-7   IO_ERROR
-8   TIMEOUT
```

### Datei-Fehler
```
-20  FILE_EXISTS
-21  IS_DIRECTORY
-22  NOT_DIRECTORY
-23  PATH_NOT_FOUND
-24  DIR_NOT_EMPTY
```

### Prozess/Thread-Fehler
```
-40  INVALID_PRIORITY
-41  NO_CHILD_PROCESSES
-42  INVALID_STATE
-43  DEADLOCK
```

### Geräte-Fehler
```
-60  DEVICE_NOT_FOUND
-61  INVALID_DEVICE
```

### GUI/TUI-Fehler
```
-100 REQUIRES_LOCK
-101 LOCK_TIMEOUT
-102 OUT_OF_BOUNDS
-103 INVALID_COLOR
```

---

## Scope und Berechtigungen

Syscalls sind nach Zielgruppe eingeteilt:

- **Both**: Verfügbar für Programme und Services
- **Program**: Nur für normale Programme
- **Service**: Nur für Service-Prozesse

Service-Prozesse müssen mit `register_service()` registriert sein.

---

## Wichtige Konzepte

### Output-Lock (GUI/TUI)

Alle TUI-Operationen erfordern das Output-Lock, um Race Conditions zu vermeiden:

```python
# Richtig:
syscall(301)           # acquire lock
syscall(304, "Text")   # write
syscall(302)           # release lock

# Falsch (wird Fehler werfen):
syscall(304, "Text")   # REQUIRES_LOCK error
```

### Python Variable statt malloc()

Es gibt **keine malloc()/free()** Syscalls. Python verwaltet Speicher automatisch:

```python
# Python-Syntax für Variablen:
my_var = 42
my_list = [1, 2, 3]
my_dict = {"key": "value"}

# Speicher-Monitoring:
mem_info = syscall(501, pid)  # get_process_memory_usage()
free_mem = syscall(503)        # get_free_memory()
```

### DLL/Module Loading

Windows-Style dynamisches Laden:

```python
handle = syscall(401, "C:\\libs\\mylib.dll")  # load_library()
exports = syscall(406, handle)                 # get_dll_exports()
addr = syscall(410, handle, "my_function")    # get_procedure_address()
syscall(403, handle)                           # unload_library()
```

---

## Navigation

- **← Zurück**: zur Kategorie-Auswahl oben
- **Kategorien**: Verwenden Sie die Links oben um zwischen Kategorien zu navigieren
- **Nächste**: Jede Kategorien-Datei enthält Links zu verwandten Kategorien

---

**Dokumentation Version**: 1.0  
**Letztes Update**: 2026-04-23  
**Educational OS**: MyPyOS v1.0

Alle Kategorien-Dokumentationen: [01-FileIO](01-FileIO.md) | [02-ProcessManagement](02-ProcessManagement.md) | [03-GUITUIOperations](03-GUITUIOperations.md) | [04-DLLModuleLoading](04-DLLModuleLoading.md) | [05-MemoryManagement](05-MemoryManagement.md) | [06-DeviceIO](06-DeviceIO.md) | [07-SignalsIPC](07-SignalsIPC.md) | [08-Threading](08-Threading.md) | [09-TimeOperations](09-TimeOperations.md) | [10-Miscellaneous](10-Miscellaneous.md)
