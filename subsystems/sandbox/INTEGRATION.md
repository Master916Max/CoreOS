# Sandbox Integration Guide

Stand: 2026-04-25

## Ziel

Diese Datei erklaert, wie du das neue V2-Sandbox-Paket aus `subsystems/sandbox` spaeter in dein OS einbaust. Die Sandbox ist bereits als eigenstaendiges Paket umgesetzt, aber sie ist absichtlich noch nicht an `kernel.py`, `subsystems/procees_multi.py` oder `subsystems/syscall.py` verdrahtet.

Die Grundidee ist:

- Der Kernel bleibt Host und Broker.
- Gastcode laeuft nur noch im Worker-Prozess der Sandbox.
- Alle Syscalls werden vom Worker als Nachrichten an den Host geschickt.
- Der Host entscheidet zentral ueber Rechte, VFS, Handles, Locks, Services und Devices.

## Was die Sandbox bereits mitbringt

Das Paket in `subsystems/sandbox` liefert bereits:

- `SandboxManager` als zentrale Host-Fassade
- `SandboxProfile` und Default-Profile
- `SandboxSession` als Host-Runtimeobjekt
- `SandboxContext` als sichere Worker-Metadaten
- `SandboxMessage` fuer das Pipe-Protokoll
- AST-Validierung fuer Gastcode
- sicheren Worker-Namespace
- hostseitiges VFS mit Handle-Broker
- Audit-Logging
- Worker-Prozess mit `multiprocessing.get_context("spawn")`

## Spaetere Einbaupunkte im OS

Es gibt drei Hauptstellen fuer die Integration.

### 1. `kernel.py`

Hier wird die Sandbox erzeugt und an die Kernsubsysteme weitergereicht.

Vorher:

```python
self.syscall_manager = SyscallManager()
self.process_manager = ProcessManager()
```

Nachher:

```python
from subsystems.sandbox import SandboxManager

self.sandbox_manager = SandboxManager()
self.syscall_manager = SyscallManager()
self.process_manager = ProcessManager()
```

Zusaetzlich solltest du in `Kernel.create_process(...)` nicht mehr direkt Python-Code ueber `Process.load_code(...)` in einen Greenlet-Prozess geben. Stattdessen:

1. `SandboxManager.create_session(...)` aufrufen
2. Session-ID im Prozessobjekt speichern
3. Den Scheduler spaeter nur noch fuer Host-seitige Verwaltung verwenden

### 2. `subsystems/procees_multi.py`

Aktuell fuehrt `Process._laufen()` den Prozesscode direkt mit `exec(...)` im selben Interpreter aus. Genau dieser Teil muss spaeter durch die Sandbox ersetzt werden.

Vorher:

```python
exec(self.code, self.namespace)
```

Nachher:

- `Process` haelt statt rohem Python-Exec nur noch eine Referenz auf eine `SandboxSession`
- der echte Gastcode lebt im Worker-Prozess
- `Process.run(...)` oder der Scheduler schieben nicht mehr Python-Code an, sondern pumpen Sandbox-Ereignisse

Empfohlener Umbau:

1. `Process` bekommt ein Feld `sandbox_session_id`
2. `Kernel.create_process(...)` ruft `sandbox_manager.create_session(...)`
3. `sandbox_manager.start_session(...)` startet den Worker
4. Das bisherige `exec(...)` in `Process._laufen()` faellt komplett weg

## 3. `subsystems/syscall.py`

Der wichtigste Einbaupunkt ist der Syscall-Pfad.

Aktuell ruft der Prozess direkt:

```python
ret = self.syscall_mgr.handle_syscall(self.pid, syscall_id, args)
```

Mit Sandbox laeuft es spaeter so:

1. Worker sendet `syscall_request`
2. Kernel oder Scheduler ruft `sandbox_manager.poll_events(...)`
3. Fuer jedes `syscall_request`-Event:
   - `sandbox_manager.handle_syscall_request(...)`
   - oder Weiterleitung an `SyscallManager.handle_syscall(...)`
4. Ergebnis wird ueber `sandbox_manager.send_response(...)` an den Worker zurueckgeschickt

Das bedeutet:

- `SyscallManager` bleibt fachlicher Dispatcher
- `SandboxManager` wird zum Sicherheits- und Transport-Layer

## Empfohlene Integrationsreihenfolge

### Phase 1: Nur Prozessstart umstellen

Ziel:

- Prozesse werden als Sandbox-Sessions erstellt
- bestehende Greenlet-Exec-Pfade werden noch nicht voll entfernt

Schritte:

1. `SandboxManager` in `Kernel.__init__` erzeugen
2. `Kernel.create_process(...)` baut eine `SandboxSession`
3. Session-ID wird im Prozessobjekt gespeichert

### Phase 2: Scheduler-Pump einbauen

Ziel:

- der Host holt regelmaessig Nachrichten aus allen Workern

Schritte:

1. In der Hauptschleife oder in `Kernel.subroutines()` `sandbox_manager.poll_events(...)` aufrufen
2. `hello`, `heartbeat`, `stdout`, `stderr`, `exit`, `crash`, `timeout` auswerten
3. `syscall_request`-Nachrichten an den Host-Syscallpfad weitergeben

Minimaler Pump:

```python
for event in self.sandbox_manager.poll_events(timeout_ms=0):
    if event.type == "syscall_request":
        result = self.sandbox_manager.handle_syscall_request(
            event.session_id,
            event.request_id,
            event.payload["syscall_id"],
            tuple(event.payload["args"]),
        )
        self.sandbox_manager.send_response(event.session_id, event.request_id, result)
```

### Phase 3: Echte OS-Handler registrieren

Im Moment kennt die Sandbox nur die eingebauten Dateisyscalls `1` bis `6`. Alles andere muss spaeter vom OS registriert werden.

Das passiert ueber:

```python
self.sandbox_manager.register_syscall_handler(301, tui_acquire_handler)
self.sandbox_manager.register_syscall_handler(302, tui_release_handler)
self.sandbox_manager.register_syscall_handler(304, tui_print_handler)
```

Empfehlung:

- Datei-Syscalls `1-6` zuerst ueber den eingebauten Sandbox-VFS laufen lassen
- TUI-Syscalls danach registrieren
- Service-, DLL- und Device-Syscalls erst danach schrittweise anbinden

## TUI-Integration

Fuer die spaetere TUI-Verdrahtung solltest du die Sandbox zum Besitzer des Locking machen.

Der erste sichere Zwischenschritt:

- `SandboxManager` verwaltet Leases fuer `tui.output`
- der registrierte Handler fuer `301` prueft oder erzeugt diesen Lease
- der Handler fuer `302` gibt ihn frei
- bei `cleanup_session(...)` wird der Lease automatisch geloest

Wichtig:

- das aktuelle `self.lock = pid` aus `subsystems/tui.py` sollte spaeter nicht mehr die einzige Quelle der Wahrheit sein
- die Sandbox sollte den Besitz kennen, die TUI nur den aktuellen Effekt

## Datei-Integration

Die Sandbox bringt bereits ein hostseitiges VFS mit. Beim Einbau solltest du entscheiden, welches System spaeter "gewinnt":

- Option A: Die Sandbox bleibt fuer `open/read/write/seek/tell/close` allein verantwortlich
- Option B: Die Sandbox validiert nur und delegiert danach an deinen vorhandenen Dateitreiber

Empfehlung:

- Fuer die erste Integration Option A nutzen
- erst spaeter den vorhandenen Treiber unter den Sandbox-VFS legen

Warum:

- so vermeidest du zwei konkurrierende Pfadauflosungen
- Handle-Ownership bleibt sauber in einer Schicht

## Service-, DLL- und Device-Integration

Diese Bereiche sind noch nicht an deinen vorhandenen Code angebunden. Die Sandbox ist aber darauf vorbereitet:

- Profiles enthalten `allowed_dlls`, `allowed_devices` und `service_actions`
- `policy.py` kennt bereits Capability-Plaetze wie `dll.load` und `device.open`

Spaeterer Einbau:

1. Handler im OS definieren
2. Diese Handler per `register_syscall_handler(...)` an `SandboxManager` binden
3. In den Handlern immer nur Host-Objekte benutzen, niemals Worker-Objekte zurueckgeben

## Cleanup beim Prozessende

Das Cleanup muss spaeter zwingend an dein echtes Prozessende gekoppelt werden.

Immer aufrufen:

```python
self.sandbox_manager.terminate_session(session_id, "process terminated")
```

oder mindestens:

```python
self.sandbox_manager.cleanup_session(session_id)
```

Das ist wichtig, damit:

- offene Dateien geschlossen werden
- TUI-Leases freigegeben werden
- Pipes geschlossen werden
- Worker-Prozesse nicht haengen bleiben

## Logging und Fehlerbehandlung

Die Sandbox bringt Audit-Logging bereits mit. Beim Einbau ins OS solltest du zwei Dinge tun:

1. Audit-Records optional in dein bestehendes Logging spiegeln
2. `stdout`, `stderr`, `crash` und `timeout` sauber in Kernel-Logs uebernehmen

Empfohlene Abbildung:

- `stdout` -> Debug- oder User-Output
- `stderr` -> Warnung
- `policy_error` -> Security-Log
- `crash` -> Fehler-Log
- `timeout` -> Fehler-Log plus Prozessabbruch

## Was du beim Einbau nicht tun solltest

- Nicht gleichzeitig den alten `exec(...)`-Pfad und den neuen Worker-Pfad produktiv laufen lassen.
- Nicht Host-Objekte in den Worker schicken.
- Nicht bestehende TUI- oder Dateiklasse zur einzigen Sicherheitsquelle machen.
- Nicht anfangen, rohe Windows-Pfade im Worker zu verwenden.

## Minimaler Endzustand

Die Integration ist erfolgreich, wenn:

- Prozesscode nicht mehr direkt im Kernel-Interpreter laeuft
- der Worker nur ueber `SandboxMessage` mit dem Host spricht
- Datei-Syscalls durch das Sandbox-VFS laufen
- der Host `syscall_request` verarbeitet und Antworten zuruecksendet
- Cleanup bei Crash, Timeout und regularem Ende funktioniert

## Empfehlung fuer den ersten echten Umbau

Beginne mit genau diesem Pfad:

1. `SandboxManager` in `kernel.py` initialisieren
2. nur Datei-Syscalls `1-6` integrieren
3. Worker fuer `Init`-Prozesse verwenden
4. erst danach TUI-Lock und Ausgabe anbinden
5. danach Services, DLLs und Devices

Das ist der kleinste sinnvolle Integrationspfad, bei dem du frueh echten Sicherheitsgewinn bekommst, ohne dein komplettes OS in einem Schritt umzubauen.
