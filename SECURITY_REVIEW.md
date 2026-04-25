# Security Review

Stand: 2026-04-24

Diese Datei fasst die aktuell wichtigsten Sicherheitsprobleme im Projekt zusammen und gibt konkrete Ansätze, wie du sie beheben kannst. Die Bewertung basiert auf dem aktuellen Code-Stand im Repository, nicht auf einer theoretischen Zielarchitektur.

## Kurzfazit

Im jetzigen Zustand gibt es noch keine echte Sicherheitsgrenze zwischen "User-Prozess" und "Kernel". Untrusted Code kann aktuell mit Host-Rechten laufen. Das größte Problem ist daher nicht eine einzelne kleine Lücke, sondern dass Prozess-Isolation, Rechteprüfung und Dateisystem-Abschirmung noch nicht technisch durchgesetzt werden.

## Priorität 1: Kritische Schwachstellen

### 1. Beliebige Codeausführung durch `exec` im Prozesssystem

**Fundstellen**

- `subsystems/procees_multi.py:49`
- `subsystems/procees_multi.py:51`
- `kernel.py:90`

**Problem**

Prozesscode wird direkt mit `exec(self.code, self.namespace)` ausgeführt. Da `__builtins__` dabei nicht entfernt oder eingeschränkt wird, hat der ausgeführte Code effektiv Zugriff auf Python-Builtins und kann typischerweise weitere Module importieren, Dateien öffnen oder Systemfunktionen nutzen.

Das bedeutet:

- keine echte Sandbox
- keine User-/Kernel-Trennung
- untrusted Prozesscode ist praktisch gleichbedeutend mit Host-Code

**Risiko**

- Lesen und Schreiben beliebiger Host-Dateien
- Import von `os`, `subprocess`, `socket`, `ctypes`
- Umgehen des vorgesehenen Syscall-Systems
- komplette Kompromittierung des Host-Prozesses

**Ansatz zur Behebung**

- `exec` nicht für untrusted Prozesscode verwenden
- Stattdessen eine eigene kleine VM / Bytecode-Engine / AST-basierte Interpreter-Schicht bauen
- Wenn du bei Python bleiben willst:
  - `__builtins__` hart einschränken
  - keine Imports erlauben
  - nur explizit freigegebene Funktionen in den Namespace legen
  - Prozesscode vor Ausführung parsen und verbotene Konstrukte blockieren
- Langfristig: Prozesscode nur in einem isolierten Worker-Prozess oder Container ausführen

**Empfohlene Mindestmaßnahme**

Wenn du kurzfristig weiter mit Python-Code experimentieren willst, führe Prozesscode nur in einem stark eingeschränkten Namespace aus und entferne alle Standard-Builtins. Das ist noch keine echte Sicherheit, aber deutlich besser als der aktuelle Zustand.

### 2. Direkter Host-Dateizugriff ohne Virtualisierung oder Rechteprüfung

**Fundstellen**

- `subsystems/syscall.py:55`
- `subsystems/syscall.py:57`
- `drivers/ntfs.py:24`
- `drivers/ntfs.py:27`

**Problem**

Pfadangaben werden praktisch direkt an den Dateitreiber weitergereicht. Es gibt keine virtuelle Root, keine Pfad-Normalisierung, keine Begrenzung auf ein Sandbox-Verzeichnis und keine Prüfung, ob ein Prozess auf einen Pfad zugreifen darf.

**Risiko**

- Path Traversal
- Lesen sensibler Host-Dateien
- Schreiben in beliebige erreichbare Dateien
- Umgehen jeder logischen "OS"-Struktur im Projekt

**Ansatz zur Behebung**

- eine virtuelle Root einführen, zum Beispiel `virtual_fs/`
- alle Pfade per `pathlib.Path(...).resolve()` normalisieren
- Zugriff nur erlauben, wenn der Zielpfad innerhalb der erlaubten Root liegt
- relative Pfade nur gegen ein prozessbezogenes Working Directory auflösen
- Zugriffsmodi pro Syscall validieren

**Empfohlene Mindestmaßnahme**

Jeder Datei-Syscall muss vor dem Öffnen prüfen:

1. ist der Pfad syntaktisch gültig
2. zeigt der aufgelöste Pfad innerhalb der erlaubten Root
3. darf der aufrufende Prozess diese Operation ausführen

### 3. Unsicheres Treiber-Laden über dynamisch zusammengesetzten `exec`-String

**Fundstellen**

- `subsystems/drivers.py:11`
- `subsystems/drivers.py:15`

**Problem**

Treiber werden über einen erzeugten Python-Import-String und `exec(...)` geladen. Das ist unnötig gefährlich und ein klassischer Code-Execution-Sink.

**Risiko**

- Ausführung manipulierten Codes
- Missbrauch, sobald `name` extern steuerbar wird
- keine Whitelist, keine Signatur, keine Integritätsprüfung

**Ansatz zur Behebung**

- `exec` komplett entfernen
- stattdessen `importlib.import_module()` nutzen
- nur Treiber aus einer festen Allowlist laden
- Modulname und Klassenname nicht frei aus Input ableiten
- optional Hash-/Signaturprüfung für Treibermodule ergänzen

**Beispielrichtung**

Statt:

```python
imp_str = f"from drivers.{name.lower()} import {name.upper()} as drive"
exec(imp_str, namespace)
```

eher:

```python
ALLOWED_DRIVERS = {
    "ntfs": ("drivers.ntfs", "NTFS"),
}
```

und dann gezielt per `importlib` laden.

## Priorität 2: Hohe Schwachstellen

### 4. Keine Besitzrechte für File-Handles

**Fundstellen**

- `drivers/ntfs.py:15`
- `drivers/ntfs.py:32`
- `drivers/ntfs.py:36`
- `subsystems/syscall.py:59`

**Problem**

Dateihandles liegen global in `self.files`. Es wird nicht gespeichert, welchem Prozess ein Handle gehört. Syscalls wie `read`, `close`, `seek` und `tell` nutzen nur eine numerische Handle-ID.

**Risiko**

- ein Prozess kann fremde Handles raten
- ein Prozess kann fremde Dateien lesen oder schließen
- keine Trennung zwischen Prozessen

**Ansatz zur Behebung**

- jedes Handle an die `pid` binden
- statt `dict[int, IO]` besser z. B. `dict[int, FileHandle]` mit:
  - `owner_pid`
  - `path`
  - `mode`
  - `file_obj`
- bei jedem File-Syscall prüfen, ob `owner_pid == pid`

**Empfohlene Mindestmaßnahme**

Jeder Datei-Syscall sollte die `pid` bis in den Treiber durchreichen und Ownership prüfen, bevor das Handle benutzt wird.

### 5. Kein Rechtemodell für Syscalls

**Fundstellen**

- `subsystems/syscall.py:35`
- `subsystems/syscall.py:41`
- `System/DLLS/defindes.py:4`

**Problem**

Es gibt zwar ein semantisches Konzept von Levels wie `User`, `Services`, `Drivers`, `Kernel`, aber diese Levels werden beim Ausführen der Syscalls nicht technisch geprüft.

**Risiko**

- jeder Prozess kann jeden registrierten Syscall aufrufen
- spätere privilegierte Kernel-/Treiber-Syscalls wären sofort missbrauchbar
- Rechteeskalation ist architektonisch vorprogrammiert

**Ansatz zur Behebung**

- jedem Prozess ein Sicherheitsprofil geben
- pro Syscall Metadaten definieren:
  - minimale Sicherheitsstufe
  - benötigte Capabilities
  - erlaubte Argumentbereiche
- `handle_syscall()` muss vor Weiterleitung autorisieren

**Empfohlene Mindestmaßnahme**

Baue eine Syscall-Tabelle mit Metadaten, zum Beispiel:

```python
syscalls[1] = {
    "handler": l_open,
    "min_level": "user",
    "capabilities": ["fs.read"],
}
```

und prüfe diese Daten zentral in `handle_syscall()`.

## Priorität 3: Mittlere Schwachstellen

### 6. Log-Leak durch ungefiltertes Mitschreiben von Syscall-Argumenten

**Fundstellen**

- `subsystems/syscall.py:36`
- `kernel.py:64`

**Problem**

Syscall-Argumente werden direkt geloggt und später gesammelt ausgegeben. Falls künftig Dateipfade, Inhalte, Tokens, geheime Parameter oder Nutzerinput über Syscalls laufen, landen diese Daten ungefiltert im Log.

**Risiko**

- versehentliche Offenlegung sensibler Daten
- Debug-Output wird zum Datenleck

**Ansatz zur Behebung**

- keine rohen Nutzdaten loggen
- sensible Argumente maskieren
- pro Syscall definieren, welche Felder geloggt werden dürfen
- Debug- und Produktionslogging trennen

### 7. Denial of Service durch dauerhaftes TUI-Lock

**Fundstellen**

- `subsystems/tui.py:79`
- `subsystems/tui.py:88`
- `subsystems/tui.py:95`

**Problem**

Ein Prozess kann die TUI sperren. Wenn er abstürzt, hängt oder nie freigibt, bleiben andere Prozesse blockiert. Es gibt kein Timeout, kein Recovery und kein Cleanup beim Prozessende.

**Risiko**

- UI-Deadlock
- blockierte Prozesse
- einfacher DoS

**Ansatz zur Behebung**

- TUI-Lock beim Prozessende automatisch freigeben
- Timeout für exklusive Ressourcen einführen
- Ownership plus Watchdog nutzen
- optional statt hartem Lock lieber Message Queue / Output-Buffer pro Prozess nutzen

### 8. Boot-Code wird über relativen Pfad geladen

**Fundstellen**

- `kernel.py:88`
- `kernel.py:90`

**Problem**

`Initial/init.py` wird über einen relativen Pfad geladen. Damit hängt das Verhalten vom aktuellen Working Directory ab. Eine manipulierte Datei oder ein veränderter Startkontext kann direkt den Boot-Code beeinflussen.

**Risiko**

- unerwarteter oder manipulierter Startcode
- inkonsistentes Verhalten je nach Startumgebung

**Ansatz zur Behebung**

- Pfade immer relativ zur Datei `kernel.py` auflösen
- `Path(__file__).resolve().parent` als Basis nutzen
- optional Boot-Dateien per Hash prüfen

## Weitere technische Schwächen

### 9. Ressourcenverwaltung ist noch nicht robust

**Fundstellen**

- `drivers/ntfs.py:12`
- `drivers/ntfs.py:28`
- `drivers/ntfs.py:32`

**Probleme**

- keine Limits für offene Handles
- `close()` entfernt Handles nicht aus `self.files`
- keine saubere Aufräumlogik beim Prozessende

**Risiko**

- Handle-Leaks
- Ressourcenerschöpfung
- inkonsistenter Zustand

**Ansatz zur Behebung**

- Handle nach `close()` aus der Tabelle entfernen
- beim Terminieren eines Prozesses alle zugehörigen Handles schließen
- Maximalanzahl pro Prozess definieren

### 10. Fehlerhafte oder unvollständige I/O-Implementierung kaschiert Risiken

**Fundstellen**

- `drivers/ntfs.py:27`
- `drivers/ntfs.py:53`
- `subsystems/syscall.py:57`

**Problem**

Einige Pfade sind aktuell funktional kaputt, etwa durch ungültige Dateimodi oder nicht exakt passende Funktionssignaturen. Das verhindert einzelne Angriffe im Moment teilweise nur zufällig, ersetzt aber keine Sicherheitsmaßnahme.

**Wichtig**

Ein kaputter Codepfad ist keine Security-Grenze. Sobald die Funktion später "repariert" wird, können die strukturellen Lücken voll durchschlagen.

**Ansatz zur Behebung**

- erst Sicherheitsmodell definieren
- dann I/O-Pfade korrigieren
- keine Funktionalität freischalten, bevor Ownership, Pfadprüfung und Rechteprüfung stehen

## Empfohlene Reihenfolge für die Behebung

### Phase 1: Architektur absichern

1. `exec` für untrusted Prozesscode abschaffen oder massiv einschränken
2. Syscall-Autorisierung mit Prozess-Level und Capabilities einführen
3. Host-Dateisystem hinter eine virtuelle Root legen

### Phase 2: Dateisystem härten

1. Pfad-Normalisierung und Root-Enforcement
2. prozessgebundene File-Handles
3. Cleanup aller Handles beim Prozessende

### Phase 3: Laufzeit stabilisieren

1. TUI-Locks robust machen
2. Logging säubern
3. Limits für Prozesse, Queues und Handles einbauen

### Phase 4: Dynamisches Laden absichern

1. `exec` im Treibersystem entfernen
2. Allowlist für Treiber
3. optional Integritätsprüfung von Modulen

## Minimaler Sicherheitsstandard, den du anstreben solltest

Bevor du untrusted oder halb-untrusted Code in diesem System laufen lässt, sollten mindestens diese Bedingungen erfüllt sein:

- kein direktes `exec` von freiem Python-Code
- kein direkter Host-Dateizugriff über Syscalls
- alle File-Handles sind an eine `pid` gebunden
- alle Syscalls prüfen Rechte und Capabilities
- exklusive Ressourcen haben Cleanup und Timeouts
- Logs enthalten keine rohen sensiblen Nutzdaten

## Ehrliche Gesamteinschätzung

Für einen Prototypen ist die Richtung okay, aber sicherheitstechnisch ist das System aktuell noch offen. Wenn du dieses Projekt weiter in Richtung "OS-Simulation mit echter Trennung" entwickeln willst, solltest du zuerst die Sicherheitsarchitektur bauen und erst danach weitere Features hinzufügen. Sonst wächst die Angriffsfläche schneller als die Kontrolle darüber.
