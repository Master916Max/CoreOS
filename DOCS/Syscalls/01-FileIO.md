# File I/O & Filesystem Syscalls

**Kategorie-ID**: 1–22  
**Kategorie**: Datei- und Verzeichnisverwaltung  
**Gesamtzahl**: 22 Syscalls  
**Scope**: Program & Service

[← Übersicht](README.md) | [Nächste: Process Management →](02-ProcessManagement.md)

---

## Übersicht

Diese Kategorie enthält alle Syscalls für Dateisystem-Operationen: Datei-Operationen (öffnen, lesen, schreiben), Verzeichnisverwaltung und Dateimetadaten.

| ID | Syscall | Beschreibung |
|---|---------|------------|
| 1 | [`open`](#1-open) | Datei zum Lesen/Schreiben öffnen |
| 2 | [`close`](#2-close) | Datei-Deskriptor schließen |
| 3 | [`read`](#3-read) | Daten aus Datei lesen |
| 4 | [`write`](#4-write) | Daten in Datei schreiben |
| 5 | [`seek`](#5-seek) | Position in Datei ändern |
| 6 | [`tell`](#6-tell) | Aktuelle Position abrufen |
| 7 | [`stat`](#7-stat) | Datei-Metadaten abrufen (nach Pfad) |
| 8 | [`fstat`](#8-fstat) | Datei-Metadaten abrufen (nach FD) |
| 9 | [`mkdir`](#9-mkdir) | Verzeichnis erstellen |
| 10 | [`rmdir`](#10-rmdir) | Leeres Verzeichnis löschen |
| 11 | [`chdir`](#11-chdir) | Aktuelles Verzeichnis ändern |
| 12 | [`getcwd`](#12-getcwd) | Aktuelles Verzeichnis abrufen |
| 13 | [`opendir`](#13-opendir) | Verzeichnis öffnen |
| 14 | [`readdir`](#14-readdir) | Verzeichnis-Einträge auflisten |
| 15 | [`closedir`](#15-closedir) | Verzeichnis schließen |
| 16 | [`unlink`](#16-unlink) | Datei löschen |
| 17 | [`rename`](#17-rename) | Datei/Verzeichnis umbenennen |
| 18 | [`truncate`](#18-truncate) | Datei auf Größe kürzen |
| 19 | [`chmod`](#19-chmod) | Dateiberechtigungen ändern |
| 20 | [`chown`](#20-chown) | Besitzer/Gruppe ändern |
| 21 | [`access`](#21-access) | Zugriff auf Datei prüfen |
| 22 | [`flush`](#22-flush) | Dateipuffer in Speicher schreiben |

---

## Detaillierte Syscall-Beschreibungen

---

## 1. `open`

**Beschreibung**: Öffnet eine Datei und gibt einen Datei-Deskriptor zurück.

**Signatur**:
```
fd = open(path: str, mode: str) → int
```

**Parameter**:
- `path` (str): Absoluter oder relativer Dateipfad
- `mode` (str): Öffnungsmodus (`"r"`, `"w"`, `"a"`, `"rb"`, `"wb"`)

**Rückgabe**: 
- `int > 0`: Datei-Deskriptor bei Erfolg
- `int < 0`: Fehlercode

**Fehler**:
- `FILE_NOT_FOUND` (-4): Datei existiert nicht (im Lesemodus)
- `PERMISSION_DENIED` (-3): Keine Berechtigung für Datei
- `INVALID_MODE` (-6): Ungültiger Öffnungsmodus

**Beschreibung**:  
Öffnet eine Datei für Lese-, Schreib- oder Anhängoperationen. Der zurückgegebene Deskriptor muss für nachfolgende Operationen (`read`, `write`, `seek`, etc.) verwendet und später mit `close` geschlossen werden.

**Hinweise**:
- **Gültige Modi**: `"r"` (Lesen), `"w"` (Schreiben, überschreiben), `"a"` (Anhängen), `"rb"` (Binär-Lesen), `"wb"` (Binär-Schreiben)
- Beim Modus `"w"` wird eine existierende Datei überschrieben
- Beim Modus `"a"` wird der Schreibzeiger ans Ende der Datei bewegt
- Mehrere Deskriptoren für dieselbe Datei sind möglich
- **Wichtig**: Alle geöffneten Dateien müssen mit `close` geschlossen werden

**Siehe auch**: [`close`](#2-close), [`read`](#3-read), [`write`](#4-write)

---

## 2. `close`

**Beschreibung**: Schließt einen Datei-Deskriptor und gibt die Ressourcen frei.

**Signatur**:
```
result = close(fd: int) → int
```

**Parameter**:
- `fd` (int): Datei-Deskriptor zum Schließen

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `INVALID_FD` (-1): Deskriptor ist ungültig
- `IO_ERROR` (-7): I/O-Fehler beim Schließen

**Beschreibung**:  
Schließt einen offenen Datei-Deskriptor und gibt die zugehörigen Systemressourcen frei. Nach dem Schließen darf der Deskriptor nicht mehr verwendet werden.

**Hinweise**:
- Jeden mit `open` geöffneten Deskriptor müssen Sie mit `close` schließen
- Mehrmaliges Schließen desselben Deskriptors erzeugt einen Fehler
- Gepufferte Daten werden automatisch geschrieben (äquivalent zu `flush`)
- Am Ende eines Programms werden alle offenen Deskriptoren vom System geschlossen

**Siehe auch**: [`open`](#1-open), [`flush`](#22-flush)

---

## 3. `read`

**Beschreibung**: Liest bis zu `size` Bytes aus einer offenen Datei.

**Signatur**:
```
data = read(fd: int, size: int) → str
```

**Parameter**:
- `fd` (int): Datei-Deskriptor
- `size` (int): Maximale Anzahl Bytes zum Lesen

**Rückgabe**: 
- `str`: Gelesene Daten (kann kürzer als `size` sein)
- Leerer String: Dateiende (EOF) erreicht
- Negativ: Fehlercode

**Fehler**:
- `INVALID_FD` (-1): Deskriptor ist ungültig
- `IO_ERROR` (-7): I/O-Fehler
- `EOF` (-9): Dateiende erreicht

**Beschreibung**:  
Liest bis zu `size` Bytes von der aktuellen Position in der Datei. Der Dateizeiger wird nach dem Lesen um die Anzahl der gelesenen Bytes verschoben.

**Hinweise**:
- Tatsächlich gelesene Datenmenge kann kleiner als `size` sein
- Wiederholter Aufruf mit `size=1024` erlaubt großen Datei-Lesung in Chunks
- Bei EOF-Erreichen wird eine leere Zeichenkette zurückgegeben
- Lesemodi: `"r"`, `"rb"` erforderlich

**Siehe auch**: [`open`](#1-open), [`write`](#4-write), [`seek`](#5-seek), [`tell`](#6-tell)

---

## 4. `write`

**Beschreibung**: Schreibt Daten an die aktuelle Position in einer offenen Datei.

**Signatur**:
```
bytes_written = write(fd: int, data: str) → int
```

**Parameter**:
- `fd` (int): Datei-Deskriptor
- `data` (str): Zu schreibende Daten

**Rückgabe**: 
- `int > 0`: Anzahl geschriebener Bytes
- Negativ: Fehlercode

**Fehler**:
- `INVALID_FD` (-1): Deskriptor ist ungültig
- `IO_ERROR` (-7): I/O-Fehler
- `PERMISSION_DENIED` (-3): Keine Schreibberechtigung

**Beschreibung**:  
Schreibt Daten an die aktuelle Position in der Datei. Wenn die Datei im Anhängmodus (`"a"`) geöffnet ist, wird am Ende geschrieben.

**Hinweise**:
- Schreibmodi: `"w"`, `"a"`, `"wb"` erforderlich
- Daten werden möglicherweise gepuffert (nutzen Sie `flush` zur Sicherung)
- Wiederholte Aufrufe schreiben Daten nacheinander hintereinander
- Rückgabewert zeigt tatsächlich geschriebene Bytes (normalerweise `len(data)`)

**Siehe auch**: [`open`](#1-open), [`read`](#3-read), [`flush`](#22-flush)

---

## 5. `seek`

**Beschreibung**: Setzt die Leseposition in einer offenen Datei.

**Signatur**:
```
new_position = seek(fd: int, offset: int, whence: int) → int
```

**Parameter**:
- `fd` (int): Datei-Deskriptor
- `offset` (int): Byte-Offset (kann negativ sein)
- `whence` (int): Referenzpunkt — `0` = Anfang, `1` = aktuell, `2` = Ende

**Rückgabe**: 
- `int ≥ 0`: Neue Position ab Dateianfang
- Negativ: Fehlercode

**Fehler**:
- `INVALID_FD` (-1): Deskriptor ist ungültig
- `INVALID_OFFSET` (-6): Offset außerhalb Dateibereich
- `IO_ERROR` (-7): I/O-Fehler

**Beschreibung**:  
Verschiebt den Dateizeiger zu einer neuen Position. Nützlich für zufälliger Dateizugriff (Random Access).

**Hinweise**:
- **whence-Werte**: `0` = Anfang, `1` = aktuelle Position, `2` = Ende
- Mit `whence=2, offset=-100` springt man 100 Bytes vor das Dateiende
- Kann über Dateigrenzen hinaus gesucht werden (aktuell führt dies zu einem Fehler)
- `seek(fd, 0, 0)` setzt Dateizeiger auf den Anfang

**Siehe auch**: [`tell`](#6-tell), [`read`](#3-read), [`write`](#4-write)

---

## 6. `tell`

**Beschreibung**: Gibt die aktuelle Leseposition in einer Datei zurück.

**Signatur**:
```
position = tell(fd: int) → int
```

**Parameter**:
- `fd` (int): Datei-Deskriptor

**Rückgabe**: 
- `int ≥ 0`: Aktuelle Position ab Dateianfang (in Bytes)
- Negativ: Fehlercode

**Fehler**:
- `INVALID_FD` (-1): Deskriptor ist ungültig
- `IO_ERROR` (-7): I/O-Fehler

**Beschreibung**:  
Gibt die aktuelle Byte-Position im Dateistream zurück. Diese Position wird nach `read` oder `write` Operationen aktualisiert.

**Hinweise**:
- Position beginnt bei `0` nach `open`
- Im Anhängmodus (`"a"`) zeigt `tell` auf das Dateiende
- Kombination mit `seek` erlaubt flexibles Positionierungsmanagement
- Wird oft vor `seek` aufgerufen, um die alte Position zu speichern

**Siehe auch**: [`seek`](#5-seek), [`read`](#3-read), [`write`](#4-write)

---

## 7. `stat`

**Beschreibung**: Gibt Datei-Metadaten basierend auf einem Dateipfad zurück.

**Signatur**:
```
stats = stat(path: str) → dict
```

**Parameter**:
- `path` (str): Dateipfad

**Rückgabe**: 
- `dict`: Dateistatistiken (siehe unten)
- Negativ: Fehlercode

**Fehler**:
- `FILE_NOT_FOUND` (-4): Datei existiert nicht
- `PERMISSION_DENIED` (-3): Keine Berechtigung zum Zugriff

**Dateistatistiken** (dict-Schlüssel):
- `size` (int): Dateigröße in Bytes
- `mode` (int): Dateiberechtigungen (oktal)
- `mtime` (int): Änderungszeit (Unix-Timestamp)
- `atime` (int): Zugriffzeit
- `ctime` (int): Änderungszeit der Metadaten
- `is_file` (bool): True, wenn reguläre Datei
- `is_dir` (bool): True, wenn Verzeichnis
- `uid` (int): Besitzer-UID
- `gid` (int): Besitzer-GID

**Beschreibung**:  
Ruft Dateimetadaten ab, ohne die Datei zu öffnen. Nützlich für Dateiprüfungen und Informationsabfragen.

**Hinweise**:
- **Unterschied zu `fstat`**: `stat` benötigt den Pfad, nicht den Deskriptor
- Kann auf symlinks, reguläre Dateien und Verzeichnisse aufgerufen werden
- Funktioniert auch auf nicht geöffneten Dateien
- Nützlich für Größenabfrage, Änderungszeit-Abfrage, etc.

**Siehe auch**: [`fstat`](#8-fstat), [`open`](#1-open)

---

## 8. `fstat`

**Beschreibung**: Gibt Datei-Metadaten basierend auf einem Deskriptor zurück.

**Signatur**:
```
stats = fstat(fd: int) → dict
```

**Parameter**:
- `fd` (int): Datei-Deskriptor

**Rückgabe**: 
- `dict`: Dateistatistiken (identisch zu `stat`)
- Negativ: Fehlercode

**Fehler**:
- `INVALID_FD` (-1): Deskriptor ist ungültig

**Dateistatistiken**: Siehe [`stat`](#7-stat)

**Beschreibung**:  
Wie `stat`, aber arbeitet mit einem offenen Datei-Deskriptor statt mit Pfad.

**Hinweise**:
- Nützlich, um Dateigröße oder aktuelle Position beim Lesen zu prüfen
- Kein Fehler `PERMISSION_DENIED` (Sie haben bereits Zugriff, sonst würde `open` fehlschlagen)
- Schneller als `stat`, da keine Pfadauflösung erforderlich ist

**Siehe auch**: [`stat`](#7-stat), [`tell`](#6-tell)

---

## 9. `mkdir`

**Beschreibung**: Erstellt ein neues Verzeichnis.

**Signatur**:
```
result = mkdir(path: str, mode: int) → int
```

**Parameter**:
- `path` (str): Pfad des zu erstellenden Verzeichnisses
- `mode` (int): Dateiberechtigungen (oktal, typisch `0o755`)

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `PERMISSION_DENIED` (-3): Keine Berechtigung im übergeordneten Verzeichnis
- `FILE_EXISTS` (-20): Verzeichnis/Datei existiert bereits
- `PATH_NOT_FOUND` (-23): Übergeordnetes Verzeichnis existiert nicht

**Beschreibung**:  
Erstellt ein einzelnes neues Verzeichnis. Das übergeordnete Verzeichnis muss existieren.

**Hinweise**:
- **Keine rekursive Erstellung**: Verwenden Sie für verschachtelte Pfade mehrere `mkdir` Aufrufe
- Typische Modi: `0o755` (rwxr-xr-x), `0o700` (rwx------)
- Der `mode`-Parameter kann durch umask des Prozesses modifiziert werden
- Windows-Pfade werden unterstützt (z.B. `C:\\Users\\Max\\NewFolder`)

**Siehe auch**: [`rmdir`](#10-rmdir), [`chdir`](#11-chdir), [`stat`](#7-stat)

---

## 10. `rmdir`

**Beschreibung**: Löscht ein leeres Verzeichnis.

**Signatur**:
```
result = rmdir(path: str) → int
```

**Parameter**:
- `path` (str): Pfad des zu löschenden Verzeichnisses

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `PERMISSION_DENIED` (-3): Keine Berechtigung
- `DIR_NOT_EMPTY` (-24): Verzeichnis ist nicht leer
- `FILE_NOT_FOUND` (-4): Verzeichnis existiert nicht

**Beschreibung**:  
Löscht ein Verzeichnis, das völlig leer sein muss (keine Dateien oder Unterverzeichnisse).

**Hinweise**:
- Zum Löschen von Dateien, verwenden Sie [`unlink`](#16-unlink), nicht `rmdir`
- Zum Löschen von nicht-leeren Verzeichnissen, müssen Sie zuerst alle Inhalte löschen
- Das übergeordnete Verzeichnis muss beschreibbar sein
- Einfache Fehlerbehandlung: Zuerst alle Dateien mit `unlink` löschen, dann `rmdir`

**Siehe auch**: [`mkdir`](#9-mkdir), [`unlink`](#16-unlink), [`opendir`](#13-opendir), [`readdir`](#14-readdir)

---

## 11. `chdir`

**Beschreibung**: Ändert das aktuelle Arbeitsverzeichnis des Prozesses.

**Signatur**:
```
result = chdir(path: str) → int
```

**Parameter**:
- `path` (str): Neues Arbeitsverzeichnis

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `FILE_NOT_FOUND` (-4): Verzeichnis existiert nicht
- `PERMISSION_DENIED` (-3): Keine Zugriffsberechtigung
- `NOT_DIRECTORY` (-22): Pfad ist keine Verzeichnis

**Beschreibung**:  
Wechselt das aktuelle Arbeitsverzeichnis (CWD) des Prozesses. Relative Dateipfade werden danach relativ zu diesem Verzeichnis aufgelöst.

**Hinweise**:
- Ändert CWD **des gesamten Prozesses** (oder nur des aktuellen Threads?)
- Relative Pfade (z.B. `"file.txt"`) werden nach diesem Verzeichnis aufgelöst
- Typische Verwendung am Programmstart zum Setzen eines Basis-Verzeichnisses
- Parent-Verzeichnis (`".."`) kann verwendet werden

**Siehe auch**: [`getcwd`](#12-getcwd), [`opendir`](#13-opendir)

---

## 12. `getcwd`

**Beschreibung**: Gibt das aktuelle Arbeitsverzeichnis des Prozesses zurück.

**Signatur**:
```
cwd = getcwd() → str
```

**Parameter**: Keine

**Rückgabe**: 
- `str`: Aktuelles Arbeitsverzeichnis (absoluter Pfad)
- Negativ: Fehlercode

**Fehler**:
- `IO_ERROR` (-7): Kann CWD nicht bestimmen

**Beschreibung**:  
Ruft den aktuellen Arbeitsverzeichnis-Pfad des Prozesses ab. Wird verwendet um zu prüfen, wo sich der Prozess gerade "befindet".

**Hinweise**:
- Wird oft nach [`chdir`](#11-chdir) aufgerufen um den Erfolg zu verifizieren
- Der zurückgegebene Pfad ist absolut (z.B. `"C:\\Users\\Max\\Documents"`)
- Der Rückgabewert wird oft für relative Pfadauflösung benötigt

**Siehe auch**: [`chdir`](#11-chdir)

---

## 13. `opendir`

**Beschreibung**: Öffnet ein Verzeichnis zum Auflisten seiner Einträge.

**Signatur**:
```
dir_fd = opendir(path: str) → int
```

**Parameter**:
- `path` (str): Pfad des zu öffnenden Verzeichnisses

**Rückgabe**: 
- `int > 0`: Verzeichnis-Deskriptor
- Negativ: Fehlercode

**Fehler**:
- `FILE_NOT_FOUND` (-4): Verzeichnis existiert nicht
- `NOT_DIRECTORY` (-22): Pfad ist keine Verzeichnis
- `PERMISSION_DENIED` (-3): Keine Leseberechtigung

**Beschreibung**:  
Öffnet ein Verzeichnis ähnlich wie `open` eine Datei. Der Deskriptor wird mit [`readdir`](#14-readdir) und [`closedir`](#15-closedir) verwendet.

**Hinweise**:
- Der Rückgabewert ist ein Verzeichnis-Deskriptor (ähnlich wie Datei-Deskriptor)
- Muss mit [`closedir`](#15-closedir) geschlossen werden
- Nach dem Öffnen zeigt ein interner Zeiger auf den ersten Eintrag
- Wiederholter `readdir` Aufruf bewegt den Zeiger vorwärts

**Siehe auch**: [`readdir`](#14-readdir), [`closedir`](#15-closedir), [`getcwd`](#12-getcwd)

---

## 14. `readdir`

**Beschreibung**: Liest und gibt alle Einträge aus einem offenen Verzeichnis zurück.

**Signatur**:
```
entries = readdir(dir_fd: int) → list[dict]
```

**Parameter**:
- `dir_fd` (int): Verzeichnis-Deskriptor (von `opendir`)

**Rückgabe**: 
- `list[dict]`: Liste der Verzeichniseinträge (siehe unten)
- Negativ: Fehlercode

**Fehler**:
- `INVALID_FD` (-1): Deskriptor ist ungültig
- `IO_ERROR` (-7): I/O-Fehler beim Lesen

**Verzeichnis-Eintrag** (dict-Schlüssel):
- `name` (str): Datei-/Verzeichnisname
- `is_dir` (bool): True, wenn Verzeichnis
- `is_file` (bool): True, wenn reguläre Datei
- `size` (int): Dateigröße in Bytes
- `mtime` (int): Änderungszeit (Unix-Timestamp)

**Beschreibung**:  
Liest alle Einträge aus einem offenen Verzeichnis und gibt sie als Liste von Dicts zurück. Enthält Dateien und Unterverzeichnisse, typischerweise ohne `.` und `..`.

**Hinweise**:
- Rückgabe ist eine komplette Liste, nicht ein Iterator
- Verzeichniseinträge sind üblicherweise **nicht sortiert**
- Mit `.` und `..` (aktuelle und Eltern-Verzeichnis) ist abhängig von Implementierung
- Schleife über `entries` um alle Einträge zu verarbeiten

**Siehe auch**: [`opendir`](#13-opendir), [`closedir`](#15-closedir), [`stat`](#7-stat)

---

## 15. `closedir`

**Beschreibung**: Schließt einen offenen Verzeichnis-Deskriptor.

**Signatur**:
```
result = closedir(dir_fd: int) → int
```

**Parameter**:
- `dir_fd` (int): Verzeichnis-Deskriptor

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `INVALID_FD` (-1): Deskriptor ist ungültig
- `IO_ERROR` (-7): I/O-Fehler beim Schließen

**Beschreibung**:  
Schließt einen mit [`opendir`](#13-opendir) geöffneten Verzeichnis-Deskriptor und gibt Ressourcen frei.

**Hinweise**:
- Muss für jeden mit `opendir` geöffneten Deskriptor aufgerufen werden
- Nach dem Schließen darf der Deskriptor nicht mehr verwendet werden
- Mehrmaliges Schließen erzeugt einen Fehler

**Siehe auch**: [`opendir`](#13-opendir), [`readdir`](#14-readdir), [`close`](#2-close)

---

## 16. `unlink`

**Beschreibung**: Löscht eine Datei.

**Signatur**:
```
result = unlink(path: str) → int
```

**Parameter**:
- `path` (str): Pfad der zu löschenden Datei

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `FILE_NOT_FOUND` (-4): Datei existiert nicht
- `PERMISSION_DENIED` (-3): Keine Berechtigung zum Löschen
- `IS_DIRECTORY` (-21): Pfad ist ein Verzeichnis (verwenden Sie [`rmdir`](#10-rmdir))

**Beschreibung**:  
Löscht eine reguläre Datei. Zum Löschen von Verzeichnissen, verwenden Sie [`rmdir`](#10-rmdir).

**Hinweise**:
- Kann nicht zum Löschen von Verzeichnissen verwendet werden
- Die Datei muss nicht geschlossen sein (wird beim Löschen automatisch geschlossen)
- Der übergeordnete Verzeichnis muss beschreibbar sein
- Symlinks werden sich selbst gelöscht, nicht ihre Ziele

**Siehe auch**: [`rmdir`](#10-rmdir), [`stat`](#7-stat)

---

## 17. `rename`

**Beschreibung**: Benennt eine Datei oder ein Verzeichnis um bzw. verschiebt es.

**Signatur**:
```
result = rename(old_path: str, new_path: str) → int
```

**Parameter**:
- `old_path` (str): Aktueller Pfad (Datei oder Verzeichnis)
- `new_path` (str): Neuer Pfad

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `FILE_NOT_FOUND` (-4): `old_path` existiert nicht
- `PERMISSION_DENIED` (-3): Keine Berechtigung
- `FILE_EXISTS` (-20): `new_path` existiert bereits (auf manchen Systemen)

**Beschreibung**:  
Benennt eine Datei oder ein Verzeichnis um und/oder verschiebt es zu einem neuen Pfad.

**Hinweise**:
- Funktioniert für Dateien **und** Verzeichnisse
- Kann auch als "move" Funktion verwendet werden (z.B. `rename("C:\\file.txt", "C:\\backup\\file.txt")`)
- Auf vielen Systemen funktioniert nicht, wenn `new_path` existiert (abhängig von Betriebssystem)
- Atomare Operation (entweder ganz oder gar nicht)

**Siehe auch**: [`unlink`](#16-unlink), [`rmdir`](#10-rmdir)

---

## 18. `truncate`

**Beschreibung**: Kürzt eine Datei auf eine bestimmte Größe.

**Signatur**:
```
result = truncate(path: str, size: int) → int
```

**Parameter**:
- `path` (str): Dateipfad
- `size` (int): Neue Dateigröße in Bytes

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `FILE_NOT_FOUND` (-4): Datei existiert nicht
- `PERMISSION_DENIED` (-3): Keine Berechtigung
- `IO_ERROR` (-7): I/O-Fehler

**Beschreibung**:  
Ändert die Dateigröße auf exakt `size` Bytes. Wenn die Datei größer war, wird sie gekürzt. Wenn sie kleiner war, wird sie mit Null-Bytes gefüllt.

**Hinweise**:
- Wird oft zum Löschen des Dateiinhalts verwendet: `truncate(path, 0)`
- Zum Vergrößern einer Datei (sparse files): `truncate(path, 10000)` → 10000 Bytes mit Nullen
- Die Datei wird **nicht geöffnet**, sondern direkt nach Pfad manipuliert
- Setzt den Dateizeiger auf den Anfang (wenn die Datei später geöffnet wird)

**Siehe auch**: [`open`](#1-open), [`write`](#4-write), [`seek`](#5-seek)

---

## 19. `chmod`

**Beschreibung**: Ändert die Berechtigungen einer Datei oder eines Verzeichnisses.

**Signatur**:
```
result = chmod(path: str, mode: int) → int
```

**Parameter**:
- `path` (str): Dateipfad
- `mode` (int): Neue Berechtigungen (oktal, z.B. `0o644`, `0o755`)

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `FILE_NOT_FOUND` (-4): Datei existiert nicht
- `PERMISSION_DENIED` (-3): Keine Berechtigung (normalerweise: nicht Besitzer)

**Berechtigungen** (oktal):
- `0o644`: `-rw-r--r--` (Besitzer Lesen/Schreiben, andere Lesen)
- `0o755`: `-rwxr-xr-x` (Besitzer alles, andere Lesen/Ausführung)
- `0o600`: `-rw-------` (Nur Besitzer)
- `0o700`: `-rwx------` (Nur Besitzer, mit Ausführung)
- `0o400`: `-r--------` (Nur Lesen, Besitzer)

**Beschreibung**:  
Ändert die Dateiberechtigungen (rwx für Besitzer/Gruppe/andere). Nur der Besitzer der Datei kann dies normalerweise durchführen.

**Hinweise**:
- Berechtigungen sind **oktal** (z.B. `0o755` nicht `755`)
- Erste Ziffer für Besitzer, zweite für Gruppe, dritte für andere
- `r` (4) = Lesen, `w` (2) = Schreiben, `x` (1) = Ausführen
- Windows-Unterstützung kann begrenzt sein (typisch: nur Read-Only und Vollzugriff)
- Umask des Prozesses beeinflusst nicht `chmod` (anders als `mkdir`)

**Siehe auch**: [`chown`](#20-chown), [`stat`](#7-stat)

---

## 20. `chown`

**Beschreibung**: Ändert den Besitzer und/oder die Gruppe einer Datei.

**Signatur**:
```
result = chown(path: str, uid: int, gid: int) → int
```

**Parameter**:
- `path` (str): Dateipfad
- `uid` (int): Neue Besitzer-UID (oder `-1` zum Beibehalten)
- `gid` (int): Neue Besitzer-GID (oder `-1` zum Beibehalten)

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `FILE_NOT_FOUND` (-4): Datei existiert nicht
- `PERMISSION_DENIED` (-3): Keine Berechtigung (normalerweise: nicht Root)

**Beschreibung**:  
Ändert den Besitzer und/oder die Gruppe einer Datei. Auf POSIX-Systemen normalerweise nur von Root durchführbar.

**Hinweise**:
- Verwenden Sie `-1` für `uid` oder `gid` um diese nicht zu ändern
- Normalerweise nur Root kann Besitzer ändern
- Auf Windows-Systemen kann diese Operation nicht unterstützt sein
- Nützlich für Server/Daemon-Prozesse, die Dateiberechtigungen übernehmen

**Siehe auch**: [`chmod`](#19-chmod), [`stat`](#7-stat)

---

## 21. `access`

**Beschreibung**: Prüft, ob ein Benutzer eine bestimmte Art von Zugriff auf eine Datei hat.

**Signatur**:
```
result = access(path: str, mode: int) → int
```

**Parameter**:
- `path` (str): Dateipfad
- `mode` (int): Zugriffsmodus zu prüfen: `0` = Existiert, `1` = Ausführbar, `2` = Beschreibbar, `4` = Lesbar

**Rückgabe**: 
- `0`: Zugriff erlaubt (oder Datei existiert)
- `-1`: Zugriff verweigert (oder Datei existiert nicht)

**Fehler**: Keine (gibt nur `0` oder `-1` zurück)

**Zugriffsmodi**:
- `0`: Prüfe, ob Datei existiert
- `1`: Prüfe, ob ausführbar
- `2`: Prüfe, ob beschreibbar
- `4`: Prüfe, ob lesbar

**Beschreibung**:  
Testet, ob der aktuelle Benutzer eine bestimmte Art von Zugriff auf eine Datei hat, ohne die Datei zu öffnen. Nützlich für Fehlerbehandlung vor `open`.

**Hinweise**:
- Rückgabe ist einfach: `0` (Zugriff OK) oder `-1` (Zugriff verweigert)
- Modi können kombiniert werden (bitwise OR): z.B. `access(path, 4|2)` für Lesen + Schreiben
- Diese Funktion prüft tatsächliche Berechtigungen zum Zeitpunkt des Aufrufs
- Zwischen `access` und `open` können Berechtigungen sich ändern (TOCTOU)

**Siehe auch**: [`open`](#1-open), [`stat`](#7-stat), [`chmod`](#19-chmod)

---

## 22. `flush`

**Beschreibung**: Schreibt gepufferte Daten für einen offenen Datei-Deskriptor in den Speicher.

**Signatur**:
```
result = flush(fd: int) → int
```

**Parameter**:
- `fd` (int): Datei-Deskriptor

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `INVALID_FD` (-1): Deskriptor ist ungültig
- `IO_ERROR` (-7): I/O-Fehler beim Schreiben

**Beschreibung**:  
Schreibt alle gepufferten Daten für einen Datei-Deskriptor tatsächlich auf die Festplatte. Wird verwendet um sicherzustellen, dass Daten nach `write` nicht nur im RAM verbleiben.

**Hinweise**:
- `write` kann Daten in einen Puffer schreiben, nicht direkt auf Disk
- `flush` zwingt den Puffer zur Festplatte zu synchronisieren
- Wird automatisch bei `close` aufgerufen
- Wichtig für kritische Daten (z.B. Datenbankeinträge, Log-Dateien)
- Performance-Impakt: `flush` ist langsamer als `write`

**Siehe auch**: [`write`](#4-write), [`close`](#2-close)

---

## Error Codes (Fehler-Referenz)

| Fehler | Code | Bedeutung |
|--------|------|----------|
| `SUCCESS` | 0 | Erfolgreich |
| `INVALID_FD` | -1 | Ungültiger Datei-Deskriptor |
| `PERMISSION_DENIED` | -3 | Berechtigung verweigert |
| `FILE_NOT_FOUND` | -4 | Datei nicht gefunden |
| `INVALID_ARGUMENT` | -6 | Ungültiges Argument |
| `IO_ERROR` | -7 | Ein-/Ausgabe-Fehler |
| `FILE_EXISTS` | -20 | Datei/Verzeichnis existiert bereits |
| `IS_DIRECTORY` | -21 | Pfad ist ein Verzeichnis |
| `NOT_DIRECTORY` | -22 | Pfad ist kein Verzeichnis |
| `PATH_NOT_FOUND` | -23 | Pfad nicht gefunden |
| `DIR_NOT_EMPTY` | -24 | Verzeichnis nicht leer |

---

**Dokumentversion**: 1.0  
**Zuletzt aktualisiert**: 2026-04-24
