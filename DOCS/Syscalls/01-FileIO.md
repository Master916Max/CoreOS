# File I/O & Filesystem Syscalls

**Kategorie-ID**: 1-22  
**Scope**: Datei- und Verzeichnisverwaltung  
**Voraussetzungen**: Keine

[← Übersicht](README.md) | [Nächste: Process Management →](02-ProcessManagement.md)

---

## Übersicht

Diese Kategorie enthält alle Syscalls für Dateisystem-Operationen: Datei-Operationen (öffnen, lesen, schreiben), Verzeichnisverwaltung und Dateimetadaten.

| ID | Syscall | Beschreibung |
|---|---------|------------|
| 1 | `open` | Datei zum Lesen/Schreiben öffnen |
| 2 | `close` | Datei-Deskriptor schließen |
| 3 | `read` | Daten aus Datei lesen |
| 4 | `write` | Daten in Datei schreiben |
| 5 | `seek` | Position in Datei ändern |
| 6 | `tell` | Aktuelle Position abrufen |
| 7 | `stat` | Datei-Metadaten abrufen |
| 8 | `fstat` | Metadaten via Deskriptor |
| 9 | `mkdir` | Verzeichnis erstellen |
| 10 | `rmdir` | Leeres Verzeichnis löschen |
| 11 | `chdir` | Aktuelles Verzeichnis ändern |
| 12 | `getcwd` | Aktuelles Verzeichnis abrufen |
| 13 | `opendir` | Verzeichnis öffnen |
| 14 | `readdir` | Verzeichnis-Einträge auflisten |
| 15 | `closedir` | Verzeichnis schließen |
| 16 | `unlink` | Datei löschen |
| 17 | `rename` | Datei umbenennen |
| 18 | `truncate` | Datei auf Größe kürzen |
| 19 | `chmod` | Berechtigungen ändern |
| 20 | `chown` | Besitzer/Gruppe ändern |
| 21 | `access` | Zugriff prüfen |
| 22 | `flush` | Puffer in Datei schreiben |

---

## Detaillierte Syscall-Beschreibungen

### 1. `open` - Datei öffnen

**Parameter**: `(path: str, mode: str)`  
**Rückgabe**: `int (file descriptor)`  
**Fehler**: `FILE_NOT_FOUND`, `PERMISSION_DENIED`, `INVALID_MODE`

Öffnet eine Datei und gibt einen Datei-Deskriptor zurück.

**Gültige Modi**:
- `"r"` - Lesen
- `"w"` - Schreiben (überschreibt)
- `"a"` - Anhängen
- `"rb"` - Binär lesen
- `"wb"` - Binär schreiben

**Beispiel**:
```python
# Textdatei öffnen
fd = syscall(1, "C:\\Users\\Max\\test.txt", "r")
if fd > 0:
    print(f"Datei geöffnet: FD={fd}")
else:
    print(f"Fehler: {fd}")

# Datei zum Schreiben öffnen
fd_write = syscall(1, "C:\\output\\result.txt", "w")

# Datei im Binär-Modus öffnen
fd_bin = syscall(1, "C:\\data\\image.bin", "rb")
```

---

### 2. `close` - Datei schließen

**Parameter**: `(fd: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `INVALID_FD`, `IO_ERROR`

Schließt einen Datei-Deskriptor und gibt Ressourcen frei.

**Beispiel**:
```python
fd = syscall(1, "C:\\test.txt", "r")
# ... Datei bearbeiten ...
result = syscall(2, fd)
if result == 0:
    print("Datei geschlossen")
else:
    print(f"Fehler beim Schließen: {result}")
```

---

### 3. `read` - Daten lesen

**Parameter**: `(fd: int, size: int)`  
**Rückgabe**: `str (data)`  
**Fehler**: `INVALID_FD`, `IO_ERROR`, `EOF`

Liest bis zu `size` Bytes aus Datei.

**Beispiel**:
```python
fd = syscall(1, "C:\\Users\\Max\\data.txt", "r")

# 100 Bytes lesen
data = syscall(3, fd, 100)
print(f"Gelesen: {data}")

# Datei komplett lesen (in Chunks)
fd = syscall(1, "C:\\large_file.txt", "r")
all_data = ""
while True:
    chunk = syscall(3, fd, 1024)
    if not chunk:
        break
    all_data += chunk

syscall(2, fd)  # close
```

---

### 4. `write` - Daten schreiben

**Parameter**: `(fd: int, data: str)`  
**Rückgabe**: `int (bytes_written)`  
**Fehler**: `INVALID_FD`, `IO_ERROR`, `PERMISSION_DENIED`

Schreibt Daten in Datei.

**Beispiel**:
```python
fd = syscall(1, "C:\\output\\log.txt", "w")

# Text schreiben
bytes_written = syscall(4, fd, "Hello World!\n")
print(f"Geschrieben: {bytes_written} Bytes")

# Mehrere Zeilen
syscall(4, fd, "Zeile 1\n")
syscall(4, fd, "Zeile 2\n")
syscall(4, fd, "Zeile 3\n")

syscall(2, fd)  # close
```

---

### 5. `seek` - Position ändern

**Parameter**: `(fd: int, offset: int, whence: int)`  
**Rückgabe**: `int (new_position)`  
**Fehler**: `INVALID_FD`, `INVALID_OFFSET`, `IO_ERROR`

Setzt die Leseposition. `whence`: 0=Anfang, 1=Aktuell, 2=Ende

**Beispiel**:
```python
fd = syscall(1, "C:\\data.bin", "rb")

# Zu Anfang
pos = syscall(5, fd, 0, 0)
print(f"Position: {pos}")

# 100 Bytes vom Anfang
pos = syscall(5, fd, 100, 0)

# 50 Bytes vom Ende
pos = syscall(5, fd, -50, 2)

# Letzten 1000 Bytes lesen
syscall(5, fd, -1000, 2)
data = syscall(3, fd, 1000)

syscall(2, fd)
```

---

### 6. `tell` - Position abrufen

**Parameter**: `(fd: int)`  
**Rückgabe**: `int (position)`  
**Fehler**: `INVALID_FD`, `IO_ERROR`

Gibt die aktuelle Leseposition zurück.

**Beispiel**:
```python
fd = syscall(1, "C:\\test.txt", "r")

# Nach 50 Bytes lesen
syscall(3, fd, 50)

# Position prüfen
pos = syscall(6, fd)
print(f"Aktuelle Position: {pos}")

syscall(2, fd)
```

---

### 7. `stat` - Metadaten abrufen (Pfad)

**Parameter**: `(path: str)`  
**Rückgabe**: `dict (file_stats)`  
**Fehler**: `FILE_NOT_FOUND`, `PERMISSION_DENIED`

Gibt Datei-Informationen zurück: Größe, Änderungszeit, Berechtigungen etc.

**Beispiel**:
```python
stats = syscall(7, "C:\\Users\\Max\\file.txt")
print(f"Größe: {stats['size']} Bytes")
print(f"Geändert: {stats['mtime']}")
print(f"Berechtigungen: {stats['mode']}")
print(f"Ist Datei: {stats['is_file']}")
print(f"Ist Verzeichnis: {stats['is_dir']}")
```

---

### 8. `fstat` - Metadaten abrufen (Deskriptor)

**Parameter**: `(fd: int)`  
**Rückgabe**: `dict (file_stats)`  
**Fehler**: `INVALID_FD`

Wie `stat`, aber mit offener Datei (Deskriptor).

**Beispiel**:
```python
fd = syscall(1, "C:\\data.bin", "rb")

stats = syscall(8, fd)
print(f"Dateigröße: {stats['size']}")
print(f"Aktuell gelesen: {stats['position']}")

syscall(2, fd)
```

---

### 9. `mkdir` - Verzeichnis erstellen

**Parameter**: `(path: str, mode: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `PERMISSION_DENIED`, `FILE_EXISTS`, `PATH_NOT_FOUND`

Erstellt ein neues Verzeichnis. `mode` ist typisch 0o755.

**Beispiel**:
```python
# Einfaches Verzeichnis
result = syscall(9, "C:\\new_folder", 0o755)
if result == 0:
    print("Verzeichnis erstellt")
else:
    print(f"Fehler: {result}")

# Mit Windows-Pfad
result = syscall(9, "C:\\Users\\Max\\MyFiles", 0o755)

# Verschachtelt (Eltern müssen existieren!)
result = syscall(9, "C:\\Users\\Max\\Projects\\MyProject", 0o755)
```

---

### 10. `rmdir` - Verzeichnis löschen

**Parameter**: `(path: str)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `PERMISSION_DENIED`, `DIR_NOT_EMPTY`, `FILE_NOT_FOUND`

Löscht ein leeres Verzeichnis.

**Beispiel**:
```python
# Leeres Verzeichnis löschen
result = syscall(10, "C:\\empty_folder")
if result == 0:
    print("Verzeichnis gelöscht")
else:
    print(f"Fehler: {result}")

# Verzeichnis ist nicht leer - Fehler!
result = syscall(10, "C:\\folder_with_files")
# Gibt DIR_NOT_EMPTY Fehler zurück
```

---

### 11. `chdir` - Verzeichnis wechseln

**Parameter**: `(path: str)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `FILE_NOT_FOUND`, `PERMISSION_DENIED`, `NOT_DIRECTORY`

Wechselt zum angegebenen Verzeichnis (CWD).

**Beispiel**:
```python
# Zum Benutzer-Verzeichnis
result = syscall(11, "C:\\Users\\Max")
if result == 0:
    print("In Verzeichnis gewechselt")

# Aktuelles Verzeichnis danach abrufen
cwd = syscall(12)  # getcwd()
print(f"Jetzt in: {cwd}")

# Zu Systemordner
syscall(11, "C:\\Windows\\System32")
```

---

### 12. `getcwd` - Aktuelles Verzeichnis

**Parameter**: `()`  
**Rückgabe**: `str (current_path)`  
**Fehler**: `IO_ERROR`

Gibt das aktuelle Arbeitsverzeichnis zurück.

**Beispiel**:
```python
cwd = syscall(12)
print(f"Aktuelles Verzeichnis: {cwd}")

# In anderes Verzeichnis wechseln
syscall(11, "C:\\Users\\Max\\Documents")

# Neues Verzeichnis abrufen
new_cwd = syscall(12)
print(f"Neues Verzeichnis: {new_cwd}")
```

---

### 13. `opendir` - Verzeichnis öffnen

**Parameter**: `(path: str)`  
**Rückgabe**: `int (dir_fd)`  
**Fehler**: `FILE_NOT_FOUND`, `NOT_DIRECTORY`, `PERMISSION_DENIED`

Öffnet ein Verzeichnis zum Auflisten von Einträgen.

**Beispiel**:
```python
dir_fd = syscall(13, "C:\\Users\\Max\\Documents")
if dir_fd > 0:
    print(f"Verzeichnis geöffnet: FD={dir_fd}")
else:
    print(f"Fehler: {dir_fd}")
```

---

### 14. `readdir` - Verzeichnis auflisten

**Parameter**: `(dir_fd: int)`  
**Rückgabe**: `list (entries)`  
**Fehler**: `INVALID_FD`, `IO_ERROR`

Liest alle Einträge aus einem Verzeichnis.

**Beispiel**:
```python
dir_fd = syscall(13, "C:\\Users\\Max")

# Alle Einträge auflisten
entries = syscall(14, dir_fd)

for entry in entries:
    print(f"Name: {entry['name']}")
    print(f"  Typ: {'DIR' if entry['is_dir'] else 'FILE'}")
    print(f"  Größe: {entry['size']}")
    print()

syscall(15, dir_fd)  # closedir
```

---

### 15. `closedir` - Verzeichnis schließen

**Parameter**: `(dir_fd: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `INVALID_FD`, `IO_ERROR`

Schließt einen Verzeichnis-Deskriptor.

**Beispiel**:
```python
dir_fd = syscall(13, "C:\\folder")
entries = syscall(14, dir_fd)
result = syscall(15, dir_fd)

if result == 0:
    print("Verzeichnis geschlossen")
```

---

### 16. `unlink` - Datei löschen

**Parameter**: `(path: str)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `FILE_NOT_FOUND`, `PERMISSION_DENIED`, `IS_DIRECTORY`

Löscht eine Datei (Verzeichnis: siehe `rmdir`).

**Beispiel**:
```python
# Datei löschen
result = syscall(16, "C:\\temp\\old_file.txt")
if result == 0:
    print("Datei gelöscht")
else:
    print(f"Fehler: {result}")

# Mehrere Dateien
syscall(16, "C:\\logs\\debug.log")
syscall(16, "C:\\logs\\error.log")
```

---

### 17. `rename` - Datei umbenennen

**Parameter**: `(old_path: str, new_path: str)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `FILE_NOT_FOUND`, `PERMISSION_DENIED`, `FILE_EXISTS`

Benennt eine Datei oder ein Verzeichnis um.

**Beispiel**:
```python
# Einfach umbenennen
result = syscall(17, "C:\\file_old.txt", "C:\\file_new.txt")

# Verschieben + umbenennen
result = syscall(17, "C:\\temp\\file.txt", "C:\\archive\\file_backup.txt")

# Verzeichnis umbenennen
result = syscall(17, "C:\\OldName", "C:\\NewName")
```

---

### 18. `truncate` - Datei kürzen

**Parameter**: `(path: str, size: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `FILE_NOT_FOUND`, `PERMISSION_DENIED`, `IO_ERROR`

Setzt Dateigröße auf `size` Bytes (kürzt oder füllt mit Nullen).

**Beispiel**:
```python
# Datei auf 1000 Bytes kürzen
result = syscall(18, "C:\\file.dat", 1000)

# Datei löschen (auf 0 Bytes)
syscall(18, "C:\\temp\\cache.tmp", 0)

# Datei vergrößern (füllt mit Nullen)
syscall(18, "C:\\sparse.bin", 10000)
```

---

### 19. `chmod` - Berechtigungen ändern

**Parameter**: `(path: str, mode: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `FILE_NOT_FOUND`, `PERMISSION_DENIED`

Ändert Datei-Berechtigungen (oktal).

**Beispiel**:
```python
# Lesen/Schreiben für Besitzer
syscall(19, "C:\\file.txt", 0o644)

# Vollzugriff für Besitzer, nur Lesen für andere
syscall(19, "C:\\script.py", 0o755)

# Nur Lesen
syscall(19, "C:\\readonly.txt", 0o444)
```

---

### 20. `chown` - Besitzer ändern

**Parameter**: `(path: str, uid: int, gid: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `FILE_NOT_FOUND`, `PERMISSION_DENIED`

Ändert Besitzer und Gruppe (UID/GID).

**Beispiel**:
```python
# Besitzer und Gruppe ändern
result = syscall(20, "C:\\file.txt", 1000, 1000)

# Nur Besitzer ändern (GID = -1 für keine Änderung)
syscall(20, "C:\\file.txt", 1001, -1)
```

---

### 21. `access` - Zugriff prüfen

**Parameter**: `(path: str, mode: int)`  
**Rückgabe**: `int (0=ja, -1=nein)`  
**Fehler**: None

Prüft Zugriff ohne zu öffnen. Mode: 4=Lesen, 2=Schreiben, 1=Ausführen, 0=Existiert

**Beispiel**:
```python
# Datei existiert?
exists = syscall(21, "C:\\file.txt", 0)
print(f"Existiert: {exists == 0}")

# Lesbar?
readable = syscall(21, "C:\\file.txt", 4)

# Schreibbar?
writable = syscall(21, "C:\\file.txt", 2)

# Kombiniert
accessible = syscall(21, "C:\\file.txt", 6)  # 4+2 = Lesen + Schreiben
```

---

### 22. `flush` - Puffer schreiben

**Parameter**: `(fd: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `INVALID_FD`, `IO_ERROR`

Schreibt gepufferte Daten sofort in Datei.

**Beispiel**:
```python
fd = syscall(1, "C:\\output.txt", "w")

# Daten schreiben
syscall(4, fd, "Line 1\n")
syscall(4, fd, "Line 2\n")

# Sofort in Datei schreiben
result = syscall(22, fd)

# Mehr Daten
syscall(4, fd, "Line 3\n")
syscall(22, fd)

syscall(2, fd)  # close
```

---

## Häufige Muster

### Datei komplett lesen

```python
def read_entire_file(path):
    fd = syscall(1, path, "r")
    if fd < 0:
        return None
    
    content = ""
    while True:
        chunk = syscall(3, fd, 4096)
        if not chunk:
            break
        content += chunk
    
    syscall(2, fd)
    return content

# Anwendung
content = read_entire_file("C:\\Users\\Max\\document.txt")
print(content)
```

### Verzeichnis rekursiv traversieren

```python
def list_dir_recursive(path, indent=0):
    dir_fd = syscall(13, path)
    if dir_fd < 0:
        return
    
    entries = syscall(14, dir_fd)
    syscall(15, dir_fd)
    
    for entry in entries:
        full_path = path + "\\" + entry['name']
        print("  " * indent + entry['name'])
        
        if entry['is_dir']:
            list_dir_recursive(full_path, indent + 1)

# Anwendung
list_dir_recursive("C:\\Users\\Max")
```

### Datei zeilenweise lesen

```python
def read_lines(path):
    fd = syscall(1, path, "r")
    if fd < 0:
        return []
    
    lines = []
    buffer = ""
    
    while True:
        chunk = syscall(3, fd, 1024)
        if not chunk:
            if buffer:
                lines.append(buffer)
            break
        
        buffer += chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            lines.append(line)
    
    syscall(2, fd)
    return lines

# Anwendung
for line in read_lines("C:\\log.txt"):
    print(line)
```

---

## Verwandte Kategorien

- [← Zurück zur Übersicht](README.md)
- [Nächste: Process Management →](02-ProcessManagement.md)
- [Device I/O & Control](06-DeviceIO.md)
- [Miscellaneous](10-Miscellaneous.md)

---

**Kategorie**: File I/O & Filesystem (IDs 1-22)  
**Letztes Update**: 2026-04-23
