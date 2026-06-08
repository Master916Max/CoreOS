# Process Management Syscalls

**Kategorie-ID**: 101–134  
**Kategorie**: Prozess- und Service-Verwaltung  
**Gesamtzahl**: 34 Syscalls  
**Scope**: Program & Service

[← Übersicht](README.md) | [← Zurück: File I/O](01-FileIO.md) | [Nächste: GUI/TUI →](03-GUITUIOperations.md)

---

## Übersicht

Prozessmanagement-Syscalls für Erstellung, Steuerung, Prioritäten und Ressourcenverwaltung. Service-spezifische Operationen nur für registrierte Services verfügbar.

| ID | Syscall | Beschreibung | Scope |
|---|---------|------------|-------|
| 101 | [`create_process`](#101-create_process) | Neuen Prozess erstellen | Both |
| 102 | [`exit`](#102-exit) | Prozess beenden | Both |
| 103 | [`wait`](#103-wait) | Auf Kinder warten | Both |
| 104 | [`waitpid`](#104-waitpid) | Auf spezifischen Prozess warten | Both |
| 105 | [`getpid`](#105-getpid) | Aktuelle Prozess-ID abrufen | Both |
| 106 | [`getppid`](#106-getppid) | Eltern-Prozess-ID abrufen | Both |
| 107 | [`terminate_process`](#107-terminate_process) | Prozess beenden | Both |
| 108 | [`kill_process`](#108-kill_process) | Prozess mit Signal beenden | Both |
| 109 | [`getuid`](#109-getuid) | User-ID abrufen | Both |
| 110 | [`setuid`](#110-setuid) | User-ID ändern | Both |
| 111 | [`getgid`](#111-getgid) | Group-ID abrufen | Both |
| 112 | [`setgid`](#112-setgid) | Group-ID ändern | Both |
| 113 | [`getgroups`](#113-getgroups) | Gruppen-Memberships abrufen | Both |
| 114 | [`setgroups`](#114-setgroups) | Gruppen-Memberships ändern | Both |
| 115 | [`getpriority`](#115-getpriority) | Prozess-Priorität abrufen | Both |
| 116 | [`setpriority`](#116-setpriority) | Priorität ändern | Both |
| 117 | [`nice`](#117-nice) | Priorität erhöhen/verringern | Both |
| 118 | [`yield_cpu`](#118-yield_cpu) | CPU-Zeit freigeben | Both |
| 119 | [`get_process_env`](#119-get_process_env) | Prozess-Umgebung lesen | Both |
| 120 | [`set_process_env`](#120-set_process_env) | Umgebungsvariable für Prozess setzen | Both |
| 121 | [`getenv`](#121-getenv) | Umgebungsvariable abrufen | Both |
| 122 | [`setenv`](#122-setenv) | Umgebungsvariable setzen | Both |
| 123 | [`unsetenv`](#123-unsetenv) | Umgebungsvariable löschen | Both |
| 124 | [`get_process_state`](#124-get_process_state) | Prozess-Zustand auslesen | Both |
| 125 | [`getrusage`](#125-getrusage) | Ressourcen-Nutzung abrufen | Both |
| 126 | [`get_process_info`](#126-get_process_info) | Prozess-Informationen abrufen | Both |
| 127 | [`get_all_pids`](#127-get_all_pids) | Alle Prozess-IDs auflisten | Both |
| 128 | [`getprocesses`](#128-getprocesses) | Alle Prozesse mit Details auflisten | Both |
| 129 | [`get_parent_pid`](#129-get_parent_pid) | Eltern-PID eines Prozesses | Both |
| 130 | [`is_service`](#130-is_service) | Ist der Prozess ein Service? | Both |
| 131 | [`register_service`](#131-register_service) | Als Service registrieren | Service |
| 132 | [`unregister_service`](#132-unregister_service) | Service abmelden | Service |
| 133 | [`get_services`](#133-get_services) | Alle Services auflisten | Service |
| 134 | [`get_service_handle`](#134-get_service_handle) | Service-Handle abrufen | Service |

---

## Detaillierte Syscall-Beschreibungen

---

## 101. `create_process`

**Beschreibung**: Erstellt einen neuen Prozess mit übergebenem Python-Code.

**Signatur**:
```
pid = create_process(name: str, code: str) → int
```

**Parameter**:
- `name` (str): Name des Prozesses (für Debugging)
- `code` (str): Python-Code zum Ausführen

**Rückgabe**: 
- `int > 0`: Prozess-ID (PID) bei Erfolg
- Negativ: Fehlercode

**Fehler**:
- `INVALID_CODE` (-6): Code ist keine gültige Python-Syntax
- `RESOURCE_EXHAUSTED` (-5): Zu viele Prozesse oder kein Speicher

**Beschreibung**:  
Erstellt einen neuen, unabhängigen Prozess, der den übergebenen Python-Code ausführt. Der zurückgegebene PID kann für Prozesskontrolle (`wait`, `kill`, `terminate`) verwendet werden.

**Hinweise**:
- Der neue Prozess läuft parallel zum aufrufenden Prozess
- Prozesse teilen **nicht** den Speicher oder Variablen (separate Kontexte)
- Der Code wird als String kompiliert und ausgeführt
- Fehlerhafte Python-Syntax führt zu `INVALID_CODE`
- Prozess-Limit abhängig von Systemkonfiguration

**Siehe auch**: [`exit`](#102-exit), [`waitpid`](#104-waitpid), [`terminate_process`](#107-terminate_process)

---

## 102. `exit`

**Beschreibung**: Beendet den aktuellen Prozess mit Exit-Code.

**Signatur**:
```
exit(code: int) → void
```

**Parameter**:
- `code` (int): Exit-Code (0 = Erfolg, >0 = Fehler)

**Rückgabe**: Keine (Prozess wird beendet)

**Fehler**: Keine

**Beschreibung**:  
Beendet den ausführenden Prozess sofort. Wird von Eltern-Prozess mit [`wait`](#103-wait) oder [`waitpid`](#104-waitpid) gelesen.

**Hinweise**:
- Exit-Code 0 signalisiert Erfolg, alles andere einen Fehler
- Alle offenen Dateien werden automatisch geschlossen
- Alle Kind-Prozesse werden zum Waise (Eltern wird init-Prozess)
- Wird normalerweise am Ende eines Prozesses aufgerufen
- Ist kein Rückgabewert

**Siehe auch**: [`create_process`](#101-create_process), [`wait`](#103-wait), [`waitpid`](#104-waitpid)

---

## 103. `wait`

**Beschreibung**: Wartet, bis ein beliebiger Kind-Prozess beendet ist.

**Signatur**:
```
pid = wait() → int
```

**Parameter**: Keine

**Rückgabe**: 
- `int > 0`: PID des beendeten Kind-Prozesses
- Negativ: Fehlercode

**Fehler**:
- `NO_CHILD_PROCESSES` (-41): Keine Kind-Prozesse existieren

**Beschreibung**:  
Blockiert den aufrufenden Prozess, bis **ein beliebiger** Kind-Prozess beendet ist. Der Exit-Code des Kindes wird über die Status-Information übergeben.

**Hinweise**:
- Blockierende Operation: Prozess wartet aktiv
- Betroffen ist der **erste** beendete Kind-Prozess
- Rückgabe: PID des beendeten Kindes
- Um Prozess-Status zu erhalten, nutzen Sie zusätzliche Abfragen
- Besser: [`waitpid`](#104-waitpid) für spezifische Prozesse

**Siehe auch**: [`waitpid`](#104-waitpid), [`create_process`](#101-create_process)

---

## 104. `waitpid`

**Beschreibung**: Wartet auf einen spezifischen Prozess und ruft seinen Status ab.

**Signatur**:
```
status = waitpid(pid: int) → int
```

**Parameter**:
- `pid` (int): Prozess-ID zu warten auf

**Rückgabe**: 
- `int`: Status/Exit-Code des Prozesses
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht
- `NO_CHILD_PROCESSES` (-41): PID ist nicht Kind-Prozess

**Beschreibung**:  
Blockiert den Aufrufer, bis der spezifizierte Prozess beendet ist, und gibt seinen Exit-Code zurück.

**Hinweise**:
- Blockiert bis Prozess mit `pid` beendet ist
- Rückgabewert ist der Exit-Code des beendeten Prozesses
- Nur auf Kind-Prozesse anwendbar
- Empfohlen für Kontrol von spezifischen Prozessen
- Ist blocking-Syscall (nutzt CPU nicht)

**Siehe auch**: [`wait`](#103-wait), [`create_process`](#101-create_process), [`exit`](#102-exit)

---

## 105. `getpid`

**Beschreibung**: Gibt die Prozess-ID des aufrufenden Prozesses zurück.

**Signatur**:
```
pid = getpid() → int
```

**Parameter**: Keine

**Rückgabe**: 
- `int`: Aktuelle Prozess-ID

**Fehler**: Keine

**Beschreibung**:  
Liest die eindeutige Prozess-ID des Aufrufers. Jeder Prozess hat eine eindeutige PID.

**Hinweise**:
- Sehr schnelle Operation (keine Systemlast)
- Rückgabewert ist immer ≥ 1
- PID 0-1 sind reserviert für Kernel/init
- PIDs können wiederverwendet werden nach Prozess-Beendigung
- Häufig für Debugging und Logging verwendet

**Siehe auch**: [`getppid`](#106-getppid), [`exit`](#102-exit)

---

## 106. `getppid`

**Beschreibung**: Gibt die Prozess-ID des Eltern-Prozesses zurück.

**Signatur**:
```
ppid = getppid() → int
```

**Parameter**: Keine

**Rückgabe**: 
- `int`: Eltern-Prozess-ID

**Fehler**: Keine

**Beschreibung**:  
Ruft die PID des Prozesses ab, der den aufrufenden Prozess erstellt hat.

**Hinweise**:
- Ist schnelle Operation
- Der Eltern-Prozess kann bereits beendet sein
- Wenn Parent beendet, wird PPID auf init-Prozess gesetzt
- Nützlich für Prozess-Hierarchie-Tracking
- Wird oft mit `getpid` kombiniert für Debugging

**Siehe auch**: [`getpid`](#105-getpid), [`create_process`](#101-create_process)

---

## 107. `terminate_process`

**Beschreibung**: Beendet einen anderen Prozess sofort.

**Signatur**:
```
result = terminate_process(pid: int) → int
```

**Parameter**:
- `pid` (int): Prozess-ID zum Beenden

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht
- `PERMISSION_DENIED` (-3): Keine Berechtigung (nicht Besitzer/Root)

**Beschreibung**:  
Beendet einen laufenden Prozess sofort. Grobe Variante von `kill_process` (sendet keinen Signal, sondern forciert Beendigung).

**Hinweise**:
- Erzwingt sofortige Beendigung (keine Cleanup-Chance)
- Nur der Prozess-Besitzer oder Root kann dies tun
- Offene Dateien werden möglicherweise nicht korrekt geschlossen
- Für graceful shutdown: [`kill_process`](#108-kill_process) mit SIGTERM verwenden
- Kann zu Datenkorruption führen, wenn Prozess Schreibvorgänge durchführt

**Siehe auch**: [`kill_process`](#108-kill_process), [`exit`](#102-exit)

---

## 108. `kill_process`

**Beschreibung**: Sendet ein Signal an einen Prozess (typischerweise zum Beenden).

**Signatur**:
```
result = kill_process(pid: int, signal: int) → int
```

**Parameter**:
- `pid` (int): Prozess-ID
- `signal` (int): Signal-Nummer (15 = SIGTERM, 9 = SIGKILL, etc.)

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht
- `PERMISSION_DENIED` (-3): Keine Berechtigung
- `INVALID_SIGNAL` (-80): Signal-Nummer ungültig

**Beschreibung**:  
Sendet ein Signal an einen Prozess. Der Prozess kann das Signal behandeln oder ignorieren (außer SIGKILL). Oft verwendet zum Beenden mit Graceful Shutdown.

**Hinweise**:
- Signal 15 (SIGTERM): Freundliche Beendigung (Prozess kann aufräumen)
- Signal 9 (SIGKILL): Erzwingt Beendigung (kann nicht ignoriert werden)
- Signal 0: Prüft nur, ob Prozess existiert (kein Effekt)
- Prozess muss Signal-Handler registriert haben um zu reagieren
- Empfohlen: Erst SIGTERM senden, dann nach Timeout SIGKILL

**Siehe auch**: [`terminate_process`](#107-terminate_process), [`signal`](#704-signal) (in Signals & IPC)

---

## 109. `getuid`

**Beschreibung**: Gibt die User-ID des aufrufenden Prozesses zurück.

**Signatur**:
```
uid = getuid() → int
```

**Parameter**: Keine

**Rückgabe**: 
- `int`: User-ID (UID)

**Fehler**: Keine

**Beschreibung**:  
Ruft die numerische Benutzer-ID ab. Wird für Berechtigungsprüfungen und Audit-Logging verwendet.

**Hinweise**:
- UID 0 ist reserviert für Root
- Normale Benutzer haben UID > 0
- Schnelle Operation
- Kann sich ändern nach `setuid` Aufruf (falls Berechtigung vorhanden)
- Wichtig für Datei-Zugriffsprüfungen

**Siehe auch**: [`setuid`](#110-setuid), [`getgid`](#111-getgid)

---

## 110. `setuid`

**Beschreibung**: Ändert die User-ID des aktuellen Prozesses.

**Signatur**:
```
result = setuid(uid: int) → int
```

**Parameter**:
- `uid` (int): Neue User-ID

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `PERMISSION_DENIED` (-3): Keine Berechtigung (normalerweise nur Root kann UID ändern)

**Beschreibung**:  
Ändert die UID des Prozesses. Normalerweise nur Root kann beliebige UIDs setzen. Normale Prozesse können nur zu ihrer originalen UID zurückwechseln.

**Hinweise**:
- Kritische Sicherheits-Operation
- Nur für Root oder zum Zurücksetzen auf originale UID
- Wirkt sich auf Datei-Zugriffe ab sofort aus
- Wird oft in Daemon-Prozessen verwendet (starten als Root, dann zu unprivilegierten User downgraden)
- Chronologisch irreversibel (Root kann zurückwechseln, normale User nicht)

**Siehe auch**: [`getuid`](#109-getuid), [`setgid`](#112-setgid)

---

## 111. `getgid`

**Beschreibung**: Gibt die Gruppen-ID des aufrufenden Prozesses zurück.

**Signatur**:
```
gid = getgid() → int
```

**Parameter**: Keine

**Rückgabe**: 
- `int`: Gruppen-ID (GID)

**Fehler**: Keine

**Beschreibung**:  
Ruft die primäre Gruppen-ID ab. Eine Prozess kann auch mehrere Gruppen gehören.

**Hinweise**:
- GID 0 ist typisch für "root"-Gruppe
- Primäre GID für Datei-Zugriffsprüfungen verwendet
- Schnelle Operation
- Siehe auch [`getgroups`](#113-getgroups) für alle Gruppen

**Siehe auch**: [`setgid`](#112-setgid), [`getuid`](#109-getuid), [`getgroups`](#113-getgroups)

---

## 112. `setgid`

**Beschreibung**: Ändert die Gruppen-ID des aktuellen Prozesses.

**Signatur**:
```
result = setgid(gid: int) → int
```

**Parameter**:
- `gid` (int): Neue Gruppen-ID

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `PERMISSION_DENIED` (-3): Keine Berechtigung

**Beschreibung**:  
Ändert die primäre GID. Wie `setuid`, normalerweise nur Root kann beliebige GIDs setzen.

**Hinweise**:
- Sicherheits-kritische Operation
- Beeinflusst Datei-Zugriffs-Berechtigungen ab sofort
- Normale User können nur zu ihrer originalen Gruppe zurück

**Siehe auch**: [`getgid`](#111-getgid), [`setuid`](#110-setuid), [`setgroups`](#114-setgroups)

---

## 113. `getgroups`

**Beschreibung**: Gibt alle Gruppen-IDs zurück, denen der Prozess angehört.

**Signatur**:
```
gids = getgroups() → list[int]
```

**Parameter**: Keine

**Rückgabe**: 
- `list[int]`: Liste aller GIDs des Prozesses

**Fehler**: Keine

**Beschreibung**:  
Ruft alle Gruppen-Memberships ab (primäre + Zusatzgruppen).

**Hinweise**:
- Typisch 1-16 Gruppen pro Prozess
- Erste Gruppe ist die primäre (von `getgid`)
- Wird für erweiterte Berechtigungsprüfungen verwendet
- Schnelle Operation

**Siehe auch**: [`setgroups`](#114-setgroups), [`getgid`](#111-getgid)

---

## 114. `setgroups`

**Beschreibung**: Setzt alle Gruppen-IDs des Prozesses.

**Signatur**:
```
result = setgroups(gids: list[int]) → int
```

**Parameter**:
- `gids` (list[int]): Liste von GIDs

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `PERMISSION_DENIED` (-3): Keine Berechtigung (nur Root)

**Beschreibung**:  
Ersetzt alle Gruppen-Memberships. Nur Root kann dies ändern.

**Hinweise**:
- Kann für spezielle Permissions-Szenarios nützlich sein
- Affektiert Datei-Zugriffsprüfungen ab sofort
- Maximum Gruppen-Limit (normalerweise 16-32)

**Siehe auch**: [`getgroups`](#113-getgroups), [`setgid`](#112-setgid)

---

## 115. `getpriority`

**Beschreibung**: Gibt die Prozess-Priorität ab.

**Signatur**:
```
priority = getpriority(pid: int) → int
```

**Parameter**:
- `pid` (int): Prozess-ID

**Rückgabe**: 
- `int` (0-255): Priorität (höher = wichtiger)
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht

**Beschreibung**:  
Ruft die aktuelle Priorität eines Prozesses ab. Höhere Werte = höhere Priorität.

**Hinweise**:
- Bereich typisch 0-255
- Wird vom Scheduler bei CPU-Verteilung berücksichtigt
- Schnelle Operation

**Siehe auch**: [`setpriority`](#116-setpriority), [`nice`](#117-nice)

---

## 116. `setpriority`

**Beschreibung**: Setzt die Prozess-Priorität.

**Signatur**:
```
result = setpriority(pid: int, priority: int) → int
```

**Parameter**:
- `pid` (int): Prozess-ID
- `priority` (int): Neue Priorität (0-255)

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht
- `INVALID_PRIORITY` (-40): Priorität außerhalb Bereich
- `PERMISSION_DENIED` (-3): Keine Berechtigung

**Beschreibung**:  
Ändert die Prozess-Priorität. Beeinflusst, wie viel CPU-Zeit der Scheduler gibt.

**Hinweise**:
- Höhere Priorität = mehr CPU-Zeit
- Nur Besitzer/Root kann ändern
- Gültig 0-255
- Änderung wirkt sofort

**Siehe auch**: [`getpriority`](#115-getpriority), [`nice`](#117-nice)

---

## 117. `nice`

**Beschreibung**: Erhöht oder verringert die Priorität relativ zur aktuellen.

**Signatur**:
```
new_priority = nice(increment: int) → int
```

**Parameter**:
- `increment` (int): Relative Änderung (positiv = weniger wichtig, negativ = wichtiger)

**Rückgabe**: 
- `int`: Neue Priorität
- Negativ: Fehlercode

**Fehler**:
- `INVALID_INCREMENT` (-6): Ungültige Änderung
- `PERMISSION_DENIED` (-3): Keine Berechtigung

**Beschreibung**:  
Macht einen Prozess "netter" (weniger CPU-Zeit) oder prioritärer. Vereinfachte Schnittstelle zu `setpriority`.

**Hinweise**:
- Positive Werte: Prozess wird weniger prioritär
- Negative Werte: Prozess wird prioritärer (Root-only)
- Häufig bei Batch-Jobs verwendet

**Siehe auch**: [`setpriority`](#116-setpriority), [`getpriority`](#115-getpriority)

---

## 118. `yield_cpu`

**Beschreibung**: Gibt die verbleibende CPU-Zeit des aktuellen Zeitslots frei.

**Signatur**:
```
result = yield_cpu() → int
```

**Parameter**: Keine

**Rückgabe**: 
- `0`: Erfolg

**Fehler**: Keine

**Beschreibung**:  
Signalisiert dem Scheduler, dass der Prozess CPU-Zeit freigibt und ein anderer Prozess ausgeführt werden kann.

**Hinweise**:
- Freiwillige Aktion (kooperativ)
- Nützlich für lange laufende Operationen
- Verhindert, dass ein Prozess die CPU "verhungert"
- Scheduler entscheidet, welcher Prozess als nächstes läuft
- Kann mehrfach aufgerufen werden

**Siehe auch**: [`setpriority`](#116-setpriority)

---

## 119. `get_process_env`

**Beschreibung**: Liest die Umgebungsvariablen eines Prozesses.

**Signatur**:
```
env = get_process_env(pid: int) → dict[str, str]
```

**Parameter**:
- `pid` (int): Prozess-ID

**Rückgabe**: 
- `dict`: Umgebungsvariablen (Key=Name, Value=Wert)
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht

**Beschreibung**:  
Ruft alle Umgebungsvariablen eines (anderen) Prozesses ab.

**Hinweise**:
- Lese-Operation (keine Änderung)
- Nützlich für Monitoring und Debugging
- Rückgabe ist Dict (oder ähnlich) mit allen Variablen

**Siehe auch**: [`set_process_env`](#120-set_process_env), [`getenv`](#121-getenv)

---

## 120. `set_process_env`

**Beschreibung**: Setzt eine Umgebungsvariable für einen Prozess.

**Signatur**:
```
result = set_process_env(pid: int, key: str, value: str) → int
```

**Parameter**:
- `pid` (int): Prozess-ID
- `key` (str): Variablenname
- `value` (str): Variablenwert

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht
- `PERMISSION_DENIED` (-3): Keine Berechtigung

**Beschreibung**:  
Setzt oder überschreibt eine Umgebungsvariable in einem anderen Prozess.

**Hinweise**:
- Ändert Prozess-Umgebung ab sofort
- Normalerweise nur Besitzer/Root kann ändern
- Wirkt sich auf Kind-Prozesse aus (Vererbung)

**Siehe auch**: [`get_process_env`](#119-get_process_env), [`setenv`](#122-setenv)

---

## 121. `getenv`

**Beschreibung**: Gibt eine Umgebungsvariable des aktuellen Prozesses zurück.

**Signatur**:
```
value = getenv(key: str) → str
```

**Parameter**:
- `key` (str): Variablenname

**Rückgabe**: 
- `str`: Variablenwert
- Negativ: Fehlercode

**Fehler**:
- `ENV_NOT_FOUND` (-9): Variable existiert nicht

**Beschreibung**:  
Liest den Wert einer Umgebungsvariable.

**Hinweise**:
- Bezieht sich auf aktuellen Prozess
- Typische Variablen: PATH, HOME, USER, etc.
- Wird oft beim Prozess-Start gesetzt
- Schnelle Operation

**Siehe auch**: [`setenv`](#122-setenv), [`get_process_env`](#119-get_process_env)

---

## 122. `setenv`

**Beschreibung**: Setzt oder überschreibt eine Umgebungsvariable.

**Signatur**:
```
result = setenv(key: str, value: str) → int
```

**Parameter**:
- `key` (str): Variablenname
- `value` (str): Variablenwert

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**: Keine (schlägt normalerweise nicht fehl)

**Beschreibung**:  
Setzt eine Umgebungsvariable im aktuellen Prozess. Wird automatisch an Kind-Prozesse vererbt.

**Hinweise**:
- Wirkt sich sofort aus
- Ist persistent bis Prozess-Ende
- Wird an alle Kind-Prozesse vererbt
- Überschreibt existierende Werte
- Keine Größenlimitierung typischerweise

**Siehe auch**: [`getenv`](#121-getenv), [`unsetenv`](#123-unsetenv)

---

## 123. `unsetenv`

**Beschreibung**: Löscht eine Umgebungsvariable.

**Signatur**:
```
result = unsetenv(key: str) → int
```

**Parameter**:
- `key` (str): Variablenname

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `ENV_NOT_FOUND` (-9): Variable existiert nicht

**Beschreibung**:  
Entfernt eine Umgebungsvariable aus dem aktuellen Prozess.

**Hinweise**:
- Wirkt sofort
- Wird an Kind-Prozesse nicht vererbt
- Kann die Variable später wieder setzen

**Siehe auch**: [`setenv`](#122-setenv), [`getenv`](#121-getenv)

---

## 124. `get_process_state`

**Beschreibung**: Gibt den aktuellen Zustand eines Prozesses ab.

**Signatur**:
```
state = get_process_state(pid: int) → str
```

**Parameter**:
- `pid` (int): Prozess-ID

**Rückgabe**: 
- `str`: Zustand ("running", "waiting", "ready", "terminated", etc.)
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht

**Beschreibung**:  
Ruft den aktuellen Scheduler-Status eines Prozesses ab.

**Hinweise**:
- Mögliche Zustände: running, ready, waiting, blocked, terminated
- Snapshot zum Abfragezeitpunkt
- Häufig für Monitoring verwendet

**Siehe auch**: [`get_process_info`](#126-get_process_info), [`getrusage`](#125-getrusage)

---

## 125. `getrusage`

**Beschreibung**: Gibt Ressourcennutzungs-Statistiken eines Prozesses ab.

**Signatur**:
```
usage = getrusage(pid: int) → dict
```

**Parameter**:
- `pid` (int): Prozess-ID

**Rückgabe**: 
- `dict`: Ressourcen-Statistiken (CPU-Zeit, Speicher, I/O, etc.)
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht

**Beschreibung**:  
Ruft detaillierte Ressourcennutzungs-Informationen ab.

**Hinweise**:
- Beinhaltet: CPU-Zeit, Speicher, Page-Faults, I/O-Operationen
- Snapshot zum Abfragezeitpunkt
- Nützlich für Performance-Monitoring
- Dict mit verschiedenen Feldern

**Siehe auch**: [`get_process_info`](#126-get_process_info), [`get_process_state`](#124-get_process_state)

---

## 126. `get_process_info`

**Beschreibung**: Gibt umfassende Informationen über einen Prozess ab.

**Signatur**:
```
info = get_process_info(pid: int) → dict
```

**Parameter**:
- `pid` (int): Prozess-ID

**Rückgabe**: 
- `dict`: Prozess-Informationen (Name, Status, Priorität, UID, GID, etc.)
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht

**Beschreibung**:  
Ruft alle verfügbaren Informationen über einen Prozess ab (kombiniert mehrere Informationen).

**Hinweise**:
- Umfassende Informationen: Name, PID, PPID, UID, GID, Status, Priorität, Speicher, CPU-Zeit, etc.
- Dict mit mehreren Feldern
- Nützlich für Prozess-Monitoring und Debugging
- Kann größere Menge Daten zurückgeben

**Siehe auch**: [`getrusage`](#125-getrusage), [`get_process_state`](#124-get_process_state)

---

## 127. `get_all_pids`

**Beschreibung**: Gibt eine Liste aller laufenden Prozess-IDs zurück.

**Signatur**:
```
pids = get_all_pids() → list[int]
```

**Parameter**: Keine

**Rückgabe**: 
- `list[int]`: Liste aller PIDs

**Fehler**: Keine

**Beschreibung**:  
Ruft alle momentan laufenden Prozess-IDs ab.

**Hinweise**:
- Vollständige Liste aller Prozesse im System
- Snapshot zum Abfragezeitpunkt
- Rückgabe ist sorted oder unsorted (implementierungsabhängig)
- Nützlich für Prozess-Enumeration

**Siehe auch**: [`getprocesses`](#128-getprocesses)

---

## 128. `getprocesses`

**Beschreibung**: Gibt detaillierte Informationen über alle Prozesse ab.

**Signatur**:
```
processes = getprocesses() → list[dict]
```

**Parameter**: Keine

**Rückgabe**: 
- `list[dict]`: Liste aller Prozesse mit Informationen
- Negativ: Fehlercode

**Fehler**: Keine

**Beschreibung**:  
Ruft eine vollständige Liste aller Prozesse mit Details ab (PID, Name, Status, etc.).

**Hinweise**:
- Jeder Prozess ein Dict mit: PID, Name, Status, UID, GID, Priorität, CPU-Zeit, Speicher, etc.
- Snapshot zum Abfragezeitpunkt
- Große Datenmenge wenn viele Prozesse laufen
- Nützlich für Prozess-Monitoring-Tools

**Siehe auch**: [`get_all_pids`](#127-get_all_pids), [`get_process_info`](#126-get_process_info)

---

## 129. `get_parent_pid`

**Beschreibung**: Gibt die Eltern-PID eines spezifischen Prozesses ab.

**Signatur**:
```
ppid = get_parent_pid(pid: int) → int
```

**Parameter**:
- `pid` (int): Prozess-ID

**Rückgabe**: 
- `int`: Eltern-Prozess-ID
- Negativ: Fehlercode

**Fehler**:
- `INVALID_PID` (-2): PID existiert nicht

**Beschreibung**:  
Ruft die PID des Eltern-Prozesses eines beliebigen Prozesses ab (nicht nur des aktuellen).

**Hinweise**:
- Nützlich zur Rekonstruktion von Prozess-Hierarchien
- Eltern können bereits beendet sein (dann ist PPID auf init gesetzt)
- Schnelle Operation

**Siehe auch**: [`getppid`](#106-getppid) (für aktuellen Prozess), [`get_process_info`](#126-get_process_info)

---

## 130. `is_service`

**Beschreibung**: Prüft, ob der aktuelle Prozess ein Service ist.

**Signatur**:
```
result = is_service() → int
```

**Parameter**: Keine

**Rückgabe**: 
- `1`: Prozess ist ein registrierter Service
- `0`: Prozess ist ein normales Programm

**Fehler**: Keine

**Beschreibung**:  
Prüft, ob der Prozess als Service registriert wurde. Services haben erweiterte Rechte.

**Hinweise**:
- Schnelle Prüfung
- Services können Service-spezifische Syscalls aufrufen
- Normalerweise Daemons oder Server-Prozesse

**Siehe auch**: [`register_service`](#131-register_service)

---

## 131. `register_service`

**Beschreibung**: Registriert den aktuellen Prozess als Service.

**Signatur**:
```
result = register_service(name: str, description: str) → int
```

**Parameter**:
- `name` (str): Service-Name (eindeutig)
- `description` (str): Kurzbeschreibung

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `NOT_SERVICE` (-99): Prozess ist nicht berechtigt
- `SERVICE_EXISTS` (-99): Name existiert bereits

**Beschreibung**:  
Registriert einen Prozess als Service. Damit erhält er erweiterte Rechte und kann Service-Syscalls nutzen.

**Hinweise**:
- Permanente Registrierung (bis Prozess-Ende oder `unregister_service`)
- Service-Name muss eindeutig sein
- Typisch vom init/daemon-Prozess aufgerufen
- Nach Registration: [`get_services`](#133-get_services) zeigt den Service

**Siehe auch**: [`unregister_service`](#132-unregister_service), [`is_service`](#130-is_service)

---

## 132. `unregister_service`

**Beschreibung**: Entfernt einen Service aus der Registrierung.

**Signatur**:
```
result = unregister_service(name: str) → int
```

**Parameter**:
- `name` (str): Service-Name

**Rückgabe**: 
- `0`: Erfolg
- Negativ: Fehlercode

**Fehler**:
- `NOT_SERVICE` (-99): Service nicht registriert
- `PERMISSION_DENIED` (-3): Keine Berechtigung

**Beschreibung**:  
Entfernt einen Service aus der Registrierung. Der Prozess verliert Service-Rechte.

**Hinweise**:
- Normalerweise vom Service selbst aufgerufen
- Nach Unregistrierung verliert Service erweiterte Rechte
- Service kann neu registriert werden
- Typisch beim Herunterfahren

**Siehe auch**: [`register_service`](#131-register_service)

---

## 133. `get_services`

**Beschreibung**: Gibt eine Liste aller registrierten Services ab.

**Signatur**:
```
services = get_services() → list[dict]
```

**Parameter**: Keine

**Rückgabe**: 
- `list[dict]`: Liste aller Services mit Details
- Negativ: Fehlercode

**Fehler**: Keine

**Beschreibung**:  
Ruft alle momentan registrierten Services ab.

**Hinweise**:
- Jeder Service ein Dict: Name, Beschreibung, PID, Status, etc.
- Snapshot zum Abfragezeitpunkt
- Nützlich für Service-Management und Monitoring
- Nur Service-Scope-Aufrufen vorhanden

**Siehe auch**: [`get_service_handle`](#134-get_service_handle), [`register_service`](#131-register_service)

---

## 134. `get_service_handle`

**Beschreibung**: Ruft den Handle (Referenz) eines registrierten Services ab.

**Signatur**:
```
handle = get_service_handle(name: str) → int
```

**Parameter**:
- `name` (str): Service-Name

**Rückgabe**: 
- `int`: Service-Handle
- Negativ: Fehlercode

**Fehler**:
- `SERVICE_NOT_FOUND` (-99): Service nicht registriert

**Beschreibung**:  
Ruft einen Handle ab, um einen Service direkt anzusprechen (z.B. für IPC).

**Hinweise**:
- Handle kann für direkte Kommunikation mit Service genutzt werden
- Handle ist opaque (interne Struktur nicht relevant)
- Gültig bis Service-Unregistrierung
- Nützlich für Service-Messaging

**Siehe auch**: [`get_services`](#133-get_services), [`register_service`](#131-register_service)

---

## Error Codes (Fehler-Referenz)

| Fehler | Code | Bedeutung |
|--------|------|-----------|
| `SUCCESS` | 0 | Erfolgreich |
| `INVALID_PID` | -2 | Ungültige Prozess-ID |
| `PERMISSION_DENIED` | -3 | Berechtigung verweigert |
| `INVALID_ARGUMENT` | -6 | Ungültiges Argument |
| `IO_ERROR` | -7 | Ein-/Ausgabe-Fehler |
| `RESOURCE_EXHAUSTED` | -5 | Zu viele Prozesse oder kein Speicher |
| `INVALID_PRIORITY` | -40 | Ungültige Priorität |
| `NO_CHILD_PROCESSES` | -41 | Keine Kind-Prozesse vorhanden |
| `INVALID_SIGNAL` | -80 | Ungültige Signal-Nummer |
| `ENV_NOT_FOUND` | -9 | Umgebungsvariable nicht gefunden |
| `SERVICE_NOT_FOUND` | -99 | Service nicht registriert |

---

**Dokumentversion**: 1.0  
**Zuletzt aktualisiert**: 2026-04-24
