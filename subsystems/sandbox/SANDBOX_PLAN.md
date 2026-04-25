# Sandbox Implementierungsplan

Stand: 2026-04-24

## Ziel

Dieser Plan beschreibt, wie in `subsystems/sandbox` eine zweistufige Sandbox fuer MyPyOS aufgebaut werden soll.

- V1: harte In-Process-Haertung fuer Gastcode, Syscalls, Dateizugriff, Ressourcen und exklusive Ressourcen
- V2: echte Isolation ueber einen separaten Worker-Prozess

Wichtig:

- V1 ist nur fuer kontrollierte Programme und Entwicklung geeignet.
- V1 ist keine starke Sicherheitsgrenze gegen boesartigen Python-Code.
- Erst V2 schafft eine echte technische Trennung zwischen Kernel und Gastcode.

## Bedrohungsmodell

Die Sandbox soll in V1 nicht "alles" loesen, sondern ganz konkret diese Angriffswege erschweren oder blockieren:

- Gastcode versucht ueber `exec`, `import`, Builtins oder Objektgraphen an Host-Funktionen zu kommen.
- Gastcode versucht ueber Pfade wie `..`, `C:\`, UNC oder Reparse-Points aus einer virtuellen Root auszubrechen.
- Prozesse greifen auf fremde Handles, TUI-Locks oder spaeter Services und Devices zu.
- Prozesse erzeugen absichtlich DoS durch Endlosschleifen, Ausgabespam oder Handle-Leaks.
- sensible Nutzdaten geraten ueber Debug- oder Audit-Logs nach aussen.

Nicht Ziel von V1:

- vollwertige Isolation gegen einen entschlossenen Angreifer im selben Python-Interpreter
- kryptographisch belastbare Integritaets- oder Signaturmodelle
- Prozesssicherheit gegen lokale Manipulation des Repository-Codes

## Aktueller Zustand

Die aktuelle Codebasis hat mehrere sicherheitskritische Schwachstellen, die der Sandbox-Plan adressiert:

- Prozesscode wird direkt per `exec(...)` ausgefuehrt.
- Der Prozess-Namespace ist nicht versiegelt.
- Syscalls werden nicht zentral autorisiert.
- Dateizugriffe greifen direkt auf Host-Pfade zu.
- Dateihandles sind nicht an eine `pid` gebunden.
- TUI-Locks koennen bei Crash oder Haenger liegen bleiben.
- Logging kann spaeter sensible Argumente unmaskiert mitschreiben.

Zusaetzlich ist aktuell in `kernel.py` ein frueher `return` vorhanden. Das ist fuer die Planung wichtig, weil die Runtime-Integration erst wirksam wird, wenn der eigentliche Bootpfad wieder durchlaeuft.

## Leitprinzipien

- Kein untrusted Code bekommt direkte Python-Objekte mit Host-Rechten.
- Jede sicherheitsrelevante Entscheidung laeuft ueber eine zentrale Fassade.
- Gastpfade und Host-Pfade bleiben intern streng getrennt.
- Jeder Prozess hat einen expliziten Sicherheitskontext.
- Jede Ressource bekommt Eigentum, Limits und Cleanup.
- Jede Verweigerung muss reproduzierbar und auditierbar sein.

## Zielarchitektur

Die Sandbox wird als eigenes Subsystem mit klaren Rollen aufgebaut.

### 1. `SandboxManager`

`SandboxManager` ist die einzige Fassade, ueber die Kernel, ProcessManager und SyscallManager mit der Sandbox sprechen. Er ist absichtlich "langweilig": keine versteckten Seiteneinstiege, keine globale Logik in Fremdmodulen.

Verantwortung:

- Policy-Auswahl pro Prozess
- Erzeugen und Verwalten eines `SandboxContext`
- Validierung von Quelltext
- Aufbau eines sicheren Gast-Namespace
- Syscall-Autorisierung
- VFS- und Handle-Zugriff
- Lease-Verwaltung fuer exklusive Ressourcen
- Limits und Audit-Logging
- Cleanup beim Prozessende

Beispiel-Skelett:

```python
class SandboxManager:
    def __init__(self, profiles: dict[str, SandboxProfile]):
        self.profiles = profiles
        self.contexts: dict[int, SandboxContext] = {}

    def create_context(self, pid: int, profile_name: str) -> SandboxContext:
        profile = self.profiles[profile_name]
        context = SandboxContext.from_profile(pid, profile)
        self.contexts[pid] = context
        return context

    def validate_source(self, code: str) -> tuple[bool, str | None]:
        return SandboxValidator().validate(code)

    def build_namespace(self, pid: int) -> dict[str, object]:
        context = self.contexts[pid]
        return build_guest_namespace(self, context)
```

### 2. `SandboxProfile`

Ein Profil beschreibt, was ein Prozess darf. Wichtig ist, dass das Profil nicht nur "Level" sagt, sondern technisch pruefbare Felder enthaelt.

Empfohlene Profile:

- `program`
- `service`
- `driver`
- `kernel`

Jedes Profil enthaelt mindestens:

- `allowed_syscalls`
- `capabilities`
- `vfs_root`
- `cwd`
- `max_open_files`
- `max_output_chars`
- `max_cpu_steps`
- `max_runtime_ms`
- `allowed_dlls`
- `allowed_exports`
- `allowed_devices`
- `service_actions`

Beispiel:

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class SandboxProfile:
    name: str
    allowed_syscalls: set[int]
    capabilities: set[str]
    vfs_root: str
    cwd: str = "/"
    max_open_files: int = 16
    max_output_chars: int = 4096
    max_cpu_steps: int = 50_000
    max_runtime_ms: int = 2_000
    allowed_dlls: set[str] = field(default_factory=set)
    allowed_exports: set[str] = field(default_factory=set)
    allowed_devices: set[str] = field(default_factory=set)
    service_actions: set[str] = field(default_factory=set)
```

### 3. `SandboxContext`

Der Kontext wird pro Prozess erzeugt und speichert den laufenden Zustand. Alles, was waehrend der Laufzeit "lebt", sollte hier landen und nicht in verstreuten globalen Tabellen.

Empfohlene Felder:

- `pid`
- `profile_name`
- `caps`
- `cwd`
- `handle_table`
- `resource_leases`
- `audit_buffer`
- `limits_state`
- `terminated_reason`

Beispiel:

```python
from dataclasses import dataclass, field
from time import monotonic

@dataclass
class LimitState:
    started_at: float = field(default_factory=monotonic)
    cpu_steps: int = 0
    output_chars: int = 0

@dataclass
class HandleEntry:
    handle_id: int
    owner_pid: int
    virtual_path: str
    host_path: str
    mode: str
    file_obj: object

@dataclass
class ResourceLease:
    resource_id: str
    owner_pid: int
    expires_at: float | None
    cleanup_action: str

@dataclass
class SandboxContext:
    pid: int
    profile_name: str
    caps: set[str]
    cwd: str
    handle_table: dict[int, HandleEntry] = field(default_factory=dict)
    resource_leases: dict[str, ResourceLease] = field(default_factory=dict)
    audit_buffer: list["SandboxAuditRecord"] = field(default_factory=list)
    limits_state: LimitState = field(default_factory=LimitState)
    terminated_reason: str | None = None
```

### 4. `SandboxAuditRecord`

Audit-Logging darf kein Nebenprodukt sein. Das Record-Format muss frueh festgelegt werden, damit Logs spaeter nicht unstrukturiert und unsicher wachsen.

Empfohlene Felder:

- `pid`
- `event_type`
- `target`
- `decision`
- `reason`
- `redacted_args`
- `timestamp`

Beispiel:

```python
from dataclasses import dataclass
from time import time

@dataclass
class SandboxAuditRecord:
    pid: int
    event_type: str
    target: str
    decision: str
    reason: str
    redacted_args: object
    timestamp: float = time()
```

Hinweis:

- In echter Implementierung besser `field(default_factory=time)` statt `timestamp: float = time()`.

## Dateistruktur in `subsystems/sandbox`

Empfohlene Struktur:

- `subsystems/sandbox/SANDBOX_PLAN.md`
- `subsystems/sandbox/__init__.py`
- `subsystems/sandbox/manager.py`
- `subsystems/sandbox/policy.py`
- `subsystems/sandbox/context.py`
- `subsystems/sandbox/validator.py`
- `subsystems/sandbox/namespace.py`
- `subsystems/sandbox/vfs.py`
- `subsystems/sandbox/limits.py`
- `subsystems/sandbox/audit.py`
- `subsystems/sandbox/errors.py`
- `subsystems/sandbox/worker.py`

## Verantwortung der einzelnen Module

### `manager.py`

Enthaelt `SandboxManager` als einzige oeffentliche Einstiegsstelle fuer den Rest des Systems.

Empfohlene Aufgaben:

- Kontext anlegen und verwalten
- Policies abfragen
- Quelltext validieren
- Namespace bauen
- Syscalls autorisieren
- Pfade aufloesen
- Handles oeffnen und schliessen
- Ressourcen aufraeumen

Nicht in `manager.py` sammeln:

- konkrete AST-Node-Logik
- konkrete Path-Parsing-Details
- feste Log-String-Templates fuer alle Faelle

### `policy.py`

Enthaelt:

- `SandboxProfile`
- Default-Profile
- Mapping von Syscalls zu Capabilities
- optionale Argument-Validatoren

Wichtig:

- Policy muss deklarativ bleiben.
- Kein Code sollte "heimlich" neue Rechte vergeben, indem er die Policy ueberspringt.

Beispiel fuer Syscall-Metadaten:

```python
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class SyscallPolicy:
    scope: str
    required_capability: str | None
    arg_validator: Callable[[object], bool] | None
    resource_class: str | None
    audit_mode: str = "metadata"

FILE_OPEN_POLICY = SyscallPolicy(
    scope="both",
    required_capability="fs.open",
    arg_validator=lambda args: isinstance(args, tuple) and len(args) == 2,
    resource_class="file",
)
```

### `context.py`

Enthaelt:

- `SandboxContext`
- `HandleEntry`
- `ResourceLease`
- `LimitState`

Wichtig:

- diese Typen sollten klein und serialisierbar bleiben
- keine Methoden mit starker Business-Logik hier verstecken

### `validator.py`

Prueft AST-basiert, ob Gastcode ueberhaupt ausgefuehrt werden darf.

Empfohlener Aufbau:

- Parser-Funktion
- `NodeVisitor`, der erlaubte und verbotene Nodes prueft
- Namensregeln fuer `__dunder__`
- Rueckgabe als `tuple[bool, str | None]`

Beispiel:

```python
import ast

FORBIDDEN_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.ClassDef,
    ast.With,
    ast.Try,
    ast.Lambda,
    ast.Global,
    ast.Nonlocal,
    ast.Raise,
    ast.Delete,
    ast.Attribute,
    ast.Await,
    ast.Yield,
)

class SandboxValidator(ast.NodeVisitor):
    def validate(self, code: str) -> tuple[bool, str | None]:
        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError as exc:
            return False, f"syntax error: {exc}"

        try:
            self.visit(tree)
        except ValueError as exc:
            return False, str(exc)
        return True, None

    def generic_visit(self, node):
        if isinstance(node, FORBIDDEN_NODES):
            raise ValueError(f"forbidden node: {type(node).__name__}")
        super().generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if "__" in node.id:
            raise ValueError("dunder names are forbidden")
```

### `namespace.py`

Baut einen versiegelten Namespace fuer Gastcode auf.

Design-Regeln:

- niemals `globals()` oder `locals()` weiterreichen
- keine Manager-Objekte in den Namespace legen
- kein `__builtins__` mit dem kompletten Standardumfang
- nur primitive, explizit erlaubte Hilfen freigeben

Beispiel:

```python
SAFE_BUILTINS = {
    "len": len,
    "range": range,
    "str": str,
    "int": int,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "enumerate": enumerate,
    "min": min,
    "max": max,
    "abs": abs,
}

def build_guest_namespace(sandbox_mgr, context):
    def syscall_wrapper(syscall_id: int, *args):
        payload = args if len(args) != 1 else args[0]
        return sandbox_mgr.dispatch_syscall(context.pid, syscall_id, payload)

    return {
        "__builtins__": SAFE_BUILTINS,
        "syscall": syscall_wrapper,
        "ret": context.pid,
    }
```

### `vfs.py`

Kapselt:

- virtuelle Root
- Pfad-Normalisierung
- Windows-sichere Pfadpruefung
- Handle-Broker

Das Modul darf nie virtuelle und Host-Pfade durcheinanderwerfen. Die Kernaufgabe ist: Gastpfad rein, gepruefter Hostpfad oder Fehler raus.

Beispiel fuer Pfadauflosung:

```python
from pathlib import Path

def resolve_virtual_path(root: Path, cwd: str, virtual_path: str) -> Path:
    if virtual_path.startswith("\\\\") or ":" in virtual_path:
        raise ValueError("host path syntax is forbidden")

    if virtual_path.startswith("/"):
        relative = virtual_path.lstrip("/")
    else:
        relative = f"{cwd.strip('/')}/{virtual_path}".strip("/")

    candidate = (root / relative).resolve()
    root_resolved = root.resolve()

    if root_resolved not in candidate.parents and candidate != root_resolved:
        raise ValueError("path escapes sandbox root")

    return candidate
```

Wichtig:

- zusaetzlich Reparse-Points und Symlinks abweisen
- finalen Pfad nach dem Oeffnen erneut validieren
- Hostpfade nie an Gastcode zurueckgeben

### `limits.py`

Verantwortlich fuer:

- Laufzeitlimit
- CPU-Schrittlimit
- Output-Limits
- Handle-Limits

V1 wird hier pragmatisch sein muessen. Im selben Interpreter lassen sich Limits nicht perfekt erzwingen, aber sie koennen DoS deutlich erschweren.

Beispiel:

```python
from time import monotonic

def check_runtime_limit(context, max_runtime_ms: int) -> bool:
    runtime_ms = (monotonic() - context.limits_state.started_at) * 1000
    return runtime_ms <= max_runtime_ms

def check_handle_limit(context, max_open_files: int) -> bool:
    return len(context.handle_table) < max_open_files
```

### `audit.py`

Verantwortlich fuer:

- Audit-Eintraege
- Redaction
- Entscheidungshistorie

Minimalprinzip:

- alles, was verweigert wird, bekommt ein Audit-Event
- alles, was sicherheitsrelevant erlaubt wird, kann optional ein Audit-Event bekommen
- Nutzdaten nur in redigierter Form loggen

Beispiel:

```python
def redact_args(args):
    if isinstance(args, tuple):
        return ["<arg>" for _ in args]
    if isinstance(args, dict):
        return {key: "<redacted>" for key in args}
    return "<redacted>"
```

### `errors.py`

Kapselt Sandbox-interne Fehlergruende und mappt sie auf bestehende Fehlercodes wie:

- `PERMISSION_DENIED`
- `INVALID_ARGUMENT`
- `RESOURCE_EXHAUSTED`
- `TIMEOUT`

Empfehlung:

- interne Gruende zuerst semantisch benennen
- Mapping auf vorhandene Kernel-Fehlercodes erst am Rand machen

Beispiel:

```python
SANDBOX_ERROR_MAP = {
    "policy_denied": -3,
    "invalid_args": -6,
    "limit_reached": -5,
    "time_budget_exceeded": -8,
}
```

### `worker.py`

In V1 nur Stub und Dokumentationsanker.

In V2 enthaelt es:

- Worker-Prozess-Start
- IPC-Nachrichtenmodell
- Lifecycle-Management

Beispiel fuer einen Stub:

```python
class SandboxWorker:
    def start(self):
        raise NotImplementedError("Worker isolation belongs to V2")
```

## Oeffentliche Schnittstellen

Empfohlene Kernmethoden:

```python
SandboxManager.create_context(pid: int, profile_name: str) -> SandboxContext
SandboxManager.build_namespace(pid: int) -> dict[str, object]
SandboxManager.validate_source(code: str) -> tuple[bool, str | None]
SandboxManager.authorize_syscall(pid: int, syscall_id: int, args) -> tuple[bool, int | None]
SandboxManager.resolve_path(pid: int, virtual_path: str) -> tuple[bool, str | None, int | None]
SandboxManager.open_handle(pid: int, virtual_path: str, mode: str) -> int | int
SandboxManager.release_process(pid: int) -> None
```

Erwartetes Zusammenspiel:

```python
ok, reason = sandbox.validate_source(code)
if not ok:
    raise SandboxViolation(reason)

context = sandbox.create_context(pid, "program")
namespace = sandbox.build_namespace(pid)
exec(code, namespace)
```

Wichtige Design-Regel:

- `Kernel`, `ProcessManager` und `SyscallManager` sprechen nur mit `SandboxManager`.
- Andere Teile des Systems sollen nicht direkt in Handle-Tabellen oder Kontexte eingreifen.

## Datenfluss in V1

So soll der gesamte Ablauf fuer einen neuen Prozess aussehen:

1. `Kernel.create_process(...)` waehlt das Profil aus.
2. `SandboxManager.create_context(...)` erstellt den Sicherheitskontext.
3. Der Quelltext wird durch `SandboxValidator` geprueft.
4. Bei Erfolg baut `namespace.py` einen versiegelten Namespace.
5. Der Prozess startet mit genau diesem Namespace.
6. Jeder `syscall(...)` geht zuerst an `SandboxManager.authorize_syscall(...)`.
7. Falls der Syscall Dateizugriff betrifft, wird zuerst das VFS befragt.
8. Falls eine exklusive Ressource betroffen ist, wird ein Lease geprueft oder erzeugt.
9. Bei Prozessende werden Handles, Leases und Audit-Puffer sauber abgeraeumt.

## Integrationspunkte im bestehenden System

### 1. `kernel.py`

Geplante Anpassungen:

- `SandboxManager` in `Kernel.__init__` erzeugen
- `SandboxManager` an `SyscallManager`, `ProcessManager` und TUI anbinden
- `create_process(...)` um `profile_name` erweitern, Default `program`
- `load_init_process(...)` ueber Sandbox-Profil starten

Beispiel:

```python
class Kernel:
    def __init__(self, screen):
        self.sandbox = SandboxManager(default_profiles())
        self.syscall_manager = SyscallManager(self.sandbox)
        self.process_manager = ProcessManager(self.sandbox)
```

### 2. `subsystems/procees_multi.py`

Geplante Anpassungen:

- `Process.setup_namespace(...)` durch Sandbox-gesteuerten Startpfad ersetzen
- Quelltext vor der Ausfuehrung validieren
- Namespace nur noch ueber Sandbox aufbauen
- Schritt- und Laufzeitlimit pro Prozess abfragen
- bei Prozessende immer `SandboxManager.release_process(pid)` aufrufen

Beispiel:

```python
def load_code(self, code: str, sandbox_manager, profile_name: str):
    ok, reason = sandbox_manager.validate_source(code)
    if not ok:
        raise ValueError(f"Sandbox rejected code: {reason}")

    sandbox_manager.create_context(self.pid, profile_name)
    self.namespace = sandbox_manager.build_namespace(self.pid)
    self.code = code
```

### 3. `subsystems/syscall.py`

Geplante Anpassungen:

- jeder Syscall bekommt Metadaten:
  - `scope`
  - `required_capability`
  - `arg_validator`
  - `resource_class`
  - `audit_mode`
- `handle_syscall(...)` ruft vor jedem Dispatch `authorize_syscall(...)` auf
- Datei-Syscalls gehen zuerst durch VFS und Handle-Broker der Sandbox

Beispiel:

```python
def handle_syscall(self, pid: int, syscall_id: int, args):
    allowed, error = self.sandbox.authorize_syscall(pid, syscall_id, args)
    if not allowed:
        return error

    syscall = self.syscalls[syscall_id]
    return syscall.redirect(pid, args)
```

### 4. `subsystems/tui.py`

Geplante Anpassungen:

- TUI-Lock wird lease-faehig
- Lock wird beim Prozessende automatisch freigegeben
- wartende Prozesse bleiben sauber registriert
- optional Timeout fuer lang gehaltene Locks

Beispiel:

```python
def require_tui(self, pid):
    lease_ok = self.sandbox.acquire_lease(pid, "tui.output")
    if not lease_ok:
        self.waiting_queue.append(pid)
        self.shedueler.block_process(pid)
        return wait_result()
    self.lock = pid
    return success_result()
```

### 5. Datei-Treiber / VFS

Geplante Anpassungen:

- direkter Host-Zugriff wird durch VFS-Schicht ersetzt
- echte Dateiobjekte bleiben innerhalb der Sandbox
- Gastcode bekommt nur opake Integer-Handles

Wichtig:

- `drivers/ntfs.py` soll spaeter nicht mehr direkt ueber rohe Gastpfade entscheiden
- erst Sandbox prueft, dann darf ein Treiber oeffnen

## V1: In-Process-Sandbox

V1 ist die erste realistische Sicherheitsstufe innerhalb desselben Python-Interpreters.

### 1. AST-Validierung

Gastcode wird vor der Ausfuehrung per AST geprueft.

Mindestens verbieten:

- `Import`
- `ImportFrom`
- `ClassDef`
- `With`
- `Try`
- `Lambda`
- `Global`
- `Nonlocal`
- `Raise`
- `Delete`
- `Attribute`
- `Await`
- `Yield`

Fuer die aktuelle Programmform mindestens erlauben:

- `Module`
- `FunctionDef`
- `Return`
- `Assign`
- `Expr`
- `Name`
- `Constant`
- `Call`
- `If`
- `While`
- `For`
- `Break`
- `Continue`
- `Pass`
- `List`
- `Tuple`
- `Dict`
- `Subscript`
- `Compare`
- `BoolOp`
- `BinOp`
- `UnaryOp`
- `JoinedStr`
- `FormattedValue`

Zusatzregeln:

- keine Namen mit `__`
- keine Decorators
- keine Attributzugriffe auf Objekte
- keine Weitergabe echter Host-Objekte in den Namespace

Erweiterung fuer spaeter:

- wenn spaeter mehr Sprachbausteine freigegeben werden, muss jede neue Node-Klasse bewusst entschieden und getestet werden

### 2. Sicherer Namespace

Der Gast-Namespace enthaelt nur:

- `syscall`
- `ret`
- wenige sichere Builtins

Empfohlene erlaubte Builtins:

- `len`
- `range`
- `str`
- `int`
- `bool`
- `list`
- `dict`
- `tuple`
- `enumerate`
- `min`
- `max`
- `abs`

Explizit nicht freigeben:

- `open`
- `exec`
- `eval`
- `compile`
- `globals`
- `locals`
- `vars`
- `dir`
- `getattr`
- `setattr`
- `delattr`
- `__import__`
- `type`
- `object`

Wichtige Entscheidung:

- V1 setzt auf "sehr wenig freigeben" statt auf "viel erlauben und blacklist pflegen"

### 3. Syscall-Autorisierung

Jeder Syscall muss vor Ausfuehrung zentral geprueft werden.

Pruefreihenfolge:

1. gibt es die `pid`
2. gibt es einen gueltigen `SandboxContext`
3. ist der Syscall fuer das Profil erlaubt
4. ist die benoetigte Capability vorhanden
5. sind die Argumente formal gueltig
6. sind Limits oder Leases betroffen

Fehlerverhalten:

- fehlende Rechte -> `PERMISSION_DENIED`
- kaputte Argumente -> `INVALID_ARGUMENT`
- Limit erreicht -> `RESOURCE_EXHAUSTED`
- Zeitlimit erreicht -> `TIMEOUT`

Empfehlung:

- Autorisierung zentral vor dem Dispatch
- keine Sonderbehandlung direkt in einzelnen Treibern oder UI-Komponenten

### 4. Virtuelles Dateisystem

V1 braucht ein eigenes VFS vor dem Host-Dateisystem.

Regeln:

- jeder Prozess bekommt eine virtuelle Root
- Gastpfade duerfen relativ sein oder mit `/` beginnen
- `C:\`, UNC-Pfade und andere Host-spezifische Pfade werden abgelehnt
- `..`-Escape wird abgelehnt
- Pfade werden kanonisch aufgeloest
- Reparse-Points, Symlinks oder Junctions werden in V1 geblockt

Empfohlener Ansatz:

- interne Arbeit mit `pathlib.Path`
- virtuelle Pfade getrennt von Host-Pfaden halten
- finalen Host-Pfad nach `resolve()` gegen die erlaubte Root pruefen

Beispiel fuer oeffnen:

```python
def open_handle(self, pid: int, virtual_path: str, mode: str):
    context = self.contexts[pid]
    host_path = self.vfs.resolve_path(context, virtual_path)

    if not self.limits.check_handle_limit(context):
        return -5

    file_obj = open(host_path, mode, encoding="utf-8")
    handle_id = self.vfs.allocate_handle_id(context)
    context.handle_table[handle_id] = HandleEntry(
        handle_id=handle_id,
        owner_pid=pid,
        virtual_path=virtual_path,
        host_path=str(host_path),
        mode=mode,
        file_obj=file_obj,
    )
    return handle_id
```

### 5. Handle-Sicherheit

Dateihandles muessen prozessgebunden sein.

Jeder Handle-Eintrag enthaelt:

- `owner_pid`
- `virtual_path`
- `host_path`
- `mode`
- `file_obj`

Jede Operation `read`, `write`, `seek`, `tell`, `close` prueft:

- existiert das Handle
- gehoert es dem aufrufenden Prozess
- erlaubt der Modus die Operation

Beispiel:

```python
def get_handle(self, pid: int, handle_id: int) -> HandleEntry:
    context = self.contexts[pid]
    entry = context.handle_table.get(handle_id)
    if entry is None or entry.owner_pid != pid:
        raise PermissionError("invalid or foreign handle")
    return entry
```

### 6. Leases fuer exklusive Ressourcen

Exklusive Ressourcen wie das TUI-Lock duerfen nicht mehr einfach per Feld gesetzt werden. Die Sandbox muss der Besitzer dieser Entscheidung sein.

Ein Lease enthaelt:

- `owner_pid`
- `resource_id`
- `expires_at`
- `cleanup_action`

Verhalten:

- beim Prozessende werden alle Leases freigegeben
- bei Timeout werden Leases bereinigt
- bei Crash greift Cleanup automatisch

Beispiel:

```python
def release_process(self, pid: int) -> None:
    context = self.contexts.get(pid)
    if context is None:
        return

    for lease in context.resource_leases.values():
        self.release_lease(lease)

    for handle in list(context.handle_table.values()):
        handle.file_obj.close()

    del self.contexts[pid]
```

### 7. Limits

V1 braucht mindestens folgende Limits:

- maximale Laufzeit pro Prozess
- maximale Schrittzahl oder Traceschritte
- maximale Anzahl offener Handles
- maximale Ausgabemenge fuer TUI

Wichtig:

- In-Process-Limits mindern DoS-Risiken
- sie verhindern aber keinen vollstaendigen Interpreter-Escape

Empfehlung:

- Output-Limit direkt in `tui.print(...)`
- Handle-Limit direkt im Handle-Broker
- Laufzeitlimit vor jedem Syscall und zusaetzlich an Prozess-Resume-Punkten pruefen

### 8. Audit-Logging

Audit-Logging ist Pflicht fuer sicherheitsrelevante Entscheidungen.

Loggen:

- verweigerte Syscalls
- verweigerte Pfade
- fehlgeschlagene AST-Pruefungen
- Handle-Missbrauch
- Limit-Ueberschreitungen

Nicht loggen:

- Klartext-Secrets
- rohe Dateiinhalte
- unmaskierte Nutzdaten
- echte Host-Pfade, wenn ein virtueller Pfad ausreichend ist

Beispiel:

```python
self.audit.record(
    pid=pid,
    event_type="syscall",
    target=str(syscall_id),
    decision="deny",
    reason="missing capability",
    redacted_args=redact_args(args),
)
```

## V2: Echte Isolation mit Worker-Prozess

V2 ersetzt die In-Process-Ausfuehrung durch einen separaten Python-Worker-Prozess.

### Ziel

Gastcode laeuft nicht mehr im Kernel-Interpreter, sondern in einem eigenen Prozess.

### Kerngedanke

- Parent-Prozess bleibt Besitzer von Kernel, TUI, Host-Dateisystem, Treibern und Audit
- Worker fuehrt nur validierten Gastcode aus
- alle Syscalls gehen ueber IPC zurueck an den Parent

### IPC-Modell

Empfohlenes Nachrichtenformat:

```json
{
  "pid": 7,
  "syscall": 301,
  "args": ["hello"]
}
```

Beispiel fuer eine Python-Nachricht:

```python
message = {
    "type": "syscall",
    "pid": 7,
    "syscall_id": 301,
    "args": ["Hello"],
}
```

### Anforderungen

- Start per `spawn`
- keine Vererbung offener Dateihandles
- keine direkten Python-Objekt-Referenzen zwischen Kernel und Worker
- harter Abbruch bei Timeout, IPC-Fehler oder Crash
- vollstaendiges Cleanup im Parent

### Minimaler V2-Ablauf

1. Parent validiert Quelltext und waehlt Profil.
2. Parent startet Worker mit minimaler Startkonfiguration.
3. Worker fuehrt nur Gastcode aus.
4. Syscalls gehen als Nachrichten an den Parent.
5. Parent prueft Policy, fuehrt Aktion aus und sendet Antwort.
6. Bei Fehler oder Timeout beendet Parent den Worker und fuehrt Cleanup aus.

## Offene Schwachstellen und Gegenmassnahmen

### 1. Python-Escape in V1

Risiko:

- trotz AST-Filter bleibt In-Process-Python grundsaetzlich riskant

Gegenmassnahme:

- V1 nur fuer kontrollierte Programme
- V2 als Pflichtphase behandeln

### 2. Objektgraph-Bypass

Risiko:

- Attribute wie `().__class__` oder Introspection koennen zur Flucht benutzt werden

Gegenmassnahme:

- `Attribute` im AST verbieten
- keine Host-Objekte in den Namespace legen

### 3. Path Traversal und Windows-Reparse-Points

Risiko:

- Ausbruch aus dem VFS ueber `..`, Junctions, Symlinks oder Host-Pfadsyntax

Gegenmassnahme:

- Pfade mit `resolve()` pruefen
- Reparse-Points in V1 blockieren
- nur Ziele innerhalb der VFS-Root akzeptieren

### 4. TOCTOU zwischen Pruefung und Oeffnen

Risiko:

- Zielpfad aendert sich zwischen Check und Nutzung

Gegenmassnahme:

- finalen Pfad nach dem Oeffnen erneut validieren
- in V1 keine Umleitungen oder Reparse-Points erlauben

### 5. Fremdzugriff auf Handles

Risiko:

- globale oder erratbare Handles koennen missbraucht werden

Gegenmassnahme:

- prozesslokale Handle-Tabellen
- Ownership-Pruefung bei jeder Operation

### 6. Rechteeskalation ueber Syscalls

Risiko:

- privilegierte Syscalls koennen ohne Profil- oder Capability-Check missbraucht werden

Gegenmassnahme:

- Autorisierung ausschliesslich zentral in `handle_syscall(...)`
- keine Seiteneinstiege an der Sandbox vorbei

### 7. Denial of Service

Risiko:

- Endlosschleifen, Lock-Hunger, Handle-Leaks oder Ausgabespam

Gegenmassnahme:

- CPU-/Zeitbudget
- Output-Limits
- Handle-Limits
- Watchdog
- Auto-Cleanup

### 8. Datenleck ueber Logs

Risiko:

- Debug- oder Audit-Logs schreiben sensible Daten mit

Gegenmassnahme:

- Redaction standardmaessig aktiv
- nur Metadaten loggen

## Reihenfolge der Implementierung

### Phase 1: Grundlagen im Sandbox-Subsystem

1. Dateistruktur in `subsystems/sandbox` anlegen
2. `SandboxProfile`, `SandboxContext` und `SandboxManager` definieren
3. Fehlercodes und Audit-Struktur festlegen
4. Default-Profile in `policy.py` fest verdrahten

Ergebnis von Phase 1:

- Sandbox kann Kontexte anlegen
- aber noch kein Prozess laeuft dadurch sicherer

### Phase 2: Gastcode absichern

1. AST-Validator bauen
2. sicheren Namespace bauen
3. Prozessstart auf Sandbox-Pfad umstellen

Ergebnis von Phase 2:

- Gastcode startet nur noch nach Validierung
- aber Syscalls und Dateisystem sind noch nicht voll abgesichert

### Phase 3: Syscall-Sicherheit

1. Syscall-Metadaten definieren
2. zentrale Autorisierung einbauen
3. Argument-Validatoren ergaenzen

Ergebnis von Phase 3:

- Rechte liegen nicht mehr verteilt im Code

### Phase 4: Dateisystem absichern

1. VFS einziehen
2. Handle-Broker bauen
3. Ownership-Checks aktivieren

Ergebnis von Phase 4:

- Gastcode sieht nur noch virtuelle Pfade und opake Handles

### Phase 5: Ressourcen und Cleanup

1. TUI-Lock als Lease modellieren
2. Limits aktivieren
3. Prozessende mit vollem Cleanup verdrahten

Ergebnis von Phase 5:

- wichtige DoS- und Deadlock-Pfade sind kontrolliert

### Phase 6: V2 vorbereiten

1. `worker.py` als Stub anlegen
2. IPC-Format festlegen
3. Parent/Worker-Trennung spezifizieren

Ergebnis von Phase 6:

- Architektur ist bereit fuer echte Isolation

## Testplan

Folgende Tests sollten nach der Implementierung vorhanden sein.

### Quelltext-Validierung

- `import os` wird blockiert
- `open("x")` wird blockiert
- `eval(...)` wird blockiert
- `exec(...)` wird blockiert
- Attributzugriff wird blockiert
- einfache erlaubte Programme laufen weiter

Beispieltest:

```python
def test_validator_blocks_import():
    ok, reason = SandboxValidator().validate("import os")
    assert ok is False
    assert "Import" in reason
```

### Syscall-Sicherheit

- erlaubte Syscalls funktionieren
- verbotene Syscalls liefern `PERMISSION_DENIED`
- kaputte Argumente liefern `INVALID_ARGUMENT`

Beispieltest:

```python
def test_program_profile_cannot_call_privileged_syscall():
    ctx = sandbox.create_context(1, "program")
    allowed, error = sandbox.authorize_syscall(1, 9999, ())
    assert allowed is False
    assert error == -3
```

### VFS-Sicherheit

- relative Pfade innerhalb der Root funktionieren
- `..` wird blockiert
- `C:\...` wird blockiert
- UNC-Pfade werden blockiert
- Reparse-Points werden blockiert

Beispieltest:

```python
def test_vfs_blocks_escape():
    with pytest.raises(ValueError):
        resolve_virtual_path(root, "/", "../secret.txt")
```

### Handle-Sicherheit

- fremde Handles koennen nicht gelesen werden
- fremde Handles koennen nicht geschlossen werden
- geschlossene Handles sind ungueltig

### Lease- und Cleanup-Tests

- TUI-Lock wird korrekt erworben
- TUI-Lock wird beim regulaeren Ende freigegeben
- TUI-Lock wird bei Crash freigegeben
- wartende Prozesse werden sauber weitergefuehrt

### Limit-Tests

- zu viele offene Handles -> `RESOURCE_EXHAUSTED`
- zu viel Output -> definierter Fehler
- Laufzeitlimit -> `TIMEOUT`

### Audit-Tests

- verweigerte Aktionen tauchen im Audit auf
- sensible Daten erscheinen nicht im Klartext

## Akzeptanzkriterien

V1 gilt als erfolgreich, wenn:

- Gastcode nur noch ueber Sandbox-Validierung startet
- direkte Host-Dateizugriffe fuer Gastcode nicht mehr moeglich sind
- Dateihandles an `pid` gebunden sind
- Syscalls zentral autorisiert werden
- TUI-Locks bei Prozessende sicher freigegeben werden
- Limits und Audit fuer die wichtigsten Pfade aktiv sind

V2 gilt als erfolgreich, wenn:

- Gastcode in einem separaten Worker-Prozess laeuft
- Host-Ressourcen nur noch ueber den Parent kontrolliert werden
- Crash oder Timeout des Workers keinen offenen Kernel-Zustand hinterlaesst

## Annahmen

- Bestehende Syscall-IDs bleiben erhalten.
- Bestehende Fehlercodes sollen nach Moeglichkeit weiterverwendet werden.
- Gastprogramme sollen weiter `syscall(...)` und `ret` benutzen.
- `program` ist das Default-Profil fuer normale Prozesse.
- `service`, `driver` und `kernel` werden in V1 bereits als Policy-Profile vorgesehen, auch wenn nicht alle Manager heute voll ausgebaut sind.

## Empfehlung

Wenn du das wirklich sauber bauen willst, dann implementiere V1 nur als kontrollierte Haertung und plane V2 direkt mit ein. Die groesste Gefahr waere, V1 spaeter als "echte Sandbox" zu behandeln. Genau das sollte in Code, Doku und Runtime-Warnungen explizit ausgeschlossen werden.
