# GUI/TUI Operations Syscalls

**Kategorie-ID**: 301-326  
**Scope**: Terminal-Ausgabe und -Eingabe  
**WICHTIG**: Output-Lock erforderlich für alle Schreib-Operationen

[← Übersicht](README.md) | [← Zurück: Process Management](02-ProcessManagement.md) | [Nächste: DLL Loading →](04-DLLModuleLoading.md)

---

## Übersicht & Output-Lock

**Kritisches Konzept**: Alle TUI-Schreib-Operationen (print, clear, etc.) erfordern das Output-Lock. Dies verhindert Race Conditions zwischen mehreren Prozessen.

### Output-Lock Pattern:
```python
syscall(301)           # acquire_lock (blockiert bis verfügbar)
# ... TUI-Operationen ...
syscall(302)           # release_lock
```

| ID | Syscall | Beschreibung |
|---|---------|------------|
| 301 | `tui_acquire_output_lock` | Output-Lock exklusiv sperren |
| 302 | `tui_release_output_lock` | Output-Lock freigeben |
| 303 | `tui_print` | Text ohne Newline |
| 304 | `tui_println` | Text mit Newline |
| 305 | `tui_printf` | Formatierte Ausgabe |
| 306 | `tui_write_string` | Text an Position |
| 307 | `tui_clear_screen` | Bildschirm löschen |
| 308 | `tui_clear_line` | Zeile löschen |
| 309 | `tui_flush` | Puffer schreiben |
| 310 | `tui_set_cursor_pos` | Cursor bewegen (absolut) |
| 311 | `tui_get_cursor_pos` | Cursor-Position abrufen |
| 312 | `tui_move_cursor` | Cursor bewegen (relativ) |
| 313 | `tui_hide_cursor` | Cursor verstecken |
| 314 | `tui_show_cursor` | Cursor anzeigen |
| 315 | `tui_set_color` | Vordergrundfarbe |
| 316 | `tui_set_bg_color` | Hintergrundfarbe |
| 317 | `tui_reset_colors` | Farben zurücksetzen |
| 318 | `tui_set_bold` | Fettdruck an/aus |
| 319 | `tui_set_underline` | Unterstrichen an/aus |
| 320 | `tui_reset_formatting` | Formatierung zurücksetzen |
| 321 | `tui_read_char` | Ein Zeichen lesen |
| 322 | `tui_read_line` | Zeile lesen |
| 323 | `tui_read_key` | Taste lesen |
| 324 | `tui_get_screen_size` | Bildschirm-Größe |
| 325 | `tui_refresh` | Anzeige aktualisieren |
| 326 | `tui_is_tty` | Ist TTY verfügbar |

---

## Detaillierte Beschreibungen

### 301. `tui_acquire_output_lock` - Lock sperren

**Parameter**: `(timeout_ms: int=0)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `LOCK_TIMEOUT`, `DEADLOCK`

Sperrt Output für diesen Prozess. Andere Prozesse warten.

**Beispiel**:
```python
# Mit unbegrenztem Timeout
result = syscall(301)
if result == 0:
    print("Lock erhalten")

# Mit Timeout (1000ms)
result = syscall(301, 1000)
if result != 0:
    print("Timeout beim Lock!")
```

---

### 302. `tui_release_output_lock` - Lock freigeben

**Parameter**: `()`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `NOT_LOCKED`, `PERMISSION_DENIED`

**Beispiel**:
```python
result = syscall(302)
if result == 0:
    print("Lock freigegeben")
```

---

### 303-305. Text Ausgabe

**Parameter tui_print**: `(text: str)`  
**Parameter tui_println**: `(text: str)`  
**Parameter tui_printf**: `(format: str, args: list)`

**Alle erfordern Output-Lock!**

**Beispiel**:
```python
syscall(301)  # acquire lock

# Einfache Ausgabe
syscall(303, "Hello ")
syscall(303, "World")  # Kein Newline: "Hello World"

# Mit Newline
syscall(304, "Neue Zeile")
syscall(304, "Zweite Zeile")

# Formatiert
syscall(305, "Prozess: {0}, Speicher: {1} MB", ["Worker1", 256])

syscall(302)  # release lock
```

---

### 306. `tui_write_string` - Text an Position

**Parameter**: `(text: str, x: int, y: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `REQUIRES_LOCK`, `OUT_OF_BOUNDS`

**Beispiel**:
```python
syscall(301)  # acquire lock

# Text bei (10, 5)
syscall(306, "===== MENU =====", 10, 5)
syscall(306, "1) Start", 10, 7)
syscall(306, "2) Stop", 10, 8)
syscall(306, "3) Exit", 10, 9)

syscall(302)  # release lock
```

---

### 307-309. Bildschirm-Verwaltung

**Parameter**: `()`  
**Alle erfordern Output-Lock!**

**Beispiel**:
```python
syscall(301)  # acquire lock

# Bildschirm löschen
syscall(307)

# Text schreiben
syscall(304, "Header")

# Nur aktuelle Zeile löschen
syscall(308)

# Puffer schreiben
syscall(309)

syscall(302)  # release lock
```

---

### 310-312. Cursor-Steuerung

**Parameter set_cursor_pos**: `(x: int, y: int)`  
**Parameter get_cursor_pos**: `()`  
**Parameter move_cursor**: `(dx: int, dy: int)`

**Beispiel**:
```python
syscall(301)  # acquire lock

# Zu Position (0, 0) gehen
syscall(310, 0, 0)

# Aktuelle Position abrufen
pos = syscall(311)
print(f"Cursor bei: {pos['x']}, {pos['y']}")

# 5 Zeichen nach rechts
syscall(312, 5, 0)

# 3 Zeilen nach unten
syscall(312, 0, 3)

syscall(302)  # release lock
```

---

### 313-314. Cursor Sichtbarkeit

**Parameter**: `()`

**Beispiel**:
```python
syscall(301)  # acquire lock

# Cursor verstecken
syscall(313)

# Etwas anzeigen
syscall(304, "Bitte warten...")

# Cursor wieder anzeigen
syscall(314)

syscall(302)  # release lock
```

---

### 315-317. Farben

**Parameter set_color**: `(color: int)`  
**Parameter set_bg_color**: `(color: int)`  
**Parameter reset_colors**: `()`

**Farb-Codes**:
- 0: Schwarz, 1: Rot, 2: Grün, 3: Gelb
- 4: Blau, 5: Magenta, 6: Cyan, 7: Weiß

**Beispiel**:
```python
syscall(301)  # acquire lock

# Rote Schrift
syscall(315, 1)
syscall(304, "ERROR: Something failed")

# Grüne Schrift auf schwarzem Hintergrund
syscall(315, 2)
syscall(316, 0)
syscall(304, "SUCCESS: Operation completed")

# Zurücksetzen
syscall(317)

syscall(302)  # release lock
```

---

### 318-320. Text-Formatierung

**Parameter set_bold**: `(enable: int)`  
**Parameter set_underline**: `(enable: int)`  
**Parameter reset_formatting**: `()`

**Beispiel**:
```python
syscall(301)  # acquire lock

# Fett
syscall(318, 1)
syscall(304, "WICHTIG")

# Normal
syscall(318, 0)

# Unterstrichen
syscall(319, 1)
syscall(304, "Länk")

# Zurücksetzen
syscall(320)
syscall(304, "Normal")

syscall(302)  # release lock
```

---

### 321-323. Benutzer-Eingabe

**Parameter read_char**: `()`  
**Parameter read_line**: `()`  
**Parameter read_key**: `()`  
**Rückgabe**: `str` / `int`

**Beispiel**:
```python
# Ein Zeichen lesen
char = syscall(321)
print(f"Zeichen: {char}")

# Ganze Zeile
line = syscall(322)
print(f"Eingabe: {line}")

# Spezielle Tasten
key = syscall(323)
# Rückgabewerte: 27=ESC, 13=ENTER, etc.
```

---

### 324-326. Bildschirm-Info

**Parameter get_screen_size**: `()`  
**Parameter refresh**: `()`  
**Parameter is_tty**: `()`

**Beispiel**:
```python
# Größe abrufen
size = syscall(324)
print(f"Größe: {size['width']}x{size['height']}")

# Anzeige aktualisieren
syscall(325)

# TTY verfügbar?
is_terminal = syscall(326)
print(f"Terminal verfügbar: {is_terminal == 1}")
```

---

## Häufige Muster

### Sichere Ausgabe (mit Lock)

```python
def safe_print(text):
    syscall(301)  # acquire
    syscall(304, text)
    syscall(302)  # release

def safe_printf(fmt, args):
    syscall(301)  # acquire
    syscall(305, fmt, args)
    syscall(302)  # release
```

### Menu-System

```python
def show_menu():
    syscall(301)  # acquire
    
    syscall(307)  # clear screen
    syscall(304, "=== MAIN MENU ===")
    syscall(304, "1) Option A")
    syscall(304, "2) Option B")
    syscall(304, "3) Exit")
    
    syscall(302)  # release
    
    choice = syscall(322)  # read line
    return choice
```

### Statusanzeige

```python
def show_status(msg, color):
    syscall(301)  # acquire
    
    syscall(315, color)  # set color
    syscall(304, f"[*] {msg}")
    syscall(317)  # reset colors
    
    syscall(302)  # release
```

### Farbige Tabelle

```python
def print_colored_table(rows):
    syscall(301)  # acquire
    
    syscall(315, 3)  # yellow for header
    syscall(304, "ID | Name | Value")
    
    for i, row in enumerate(rows):
        color = 2 if i % 2 == 0 else 7  # alternating green/white
        syscall(315, color)
        syscall(305, "{0} | {1} | {2}", row)
    
    syscall(317)  # reset
    syscall(302)  # release
```

---

## Wichtige Hinweise

1. **IMMER Lock vor Schreiben**: Fehlende Locks verursachen `REQUIRES_LOCK` Fehler
2. **Lock-Timeout**: Mit `timeout_ms` in `acquire_lock()` Deadlock vermeiden
3. **Farben Terminal-abhängig**: Nicht alle Terminals unterstützen alle Farben
4. **Eingabe blockiert**: `read_line()` und `read_char()` blockieren Prozess

---

## Verwandte Kategorien

- [← Zurück: Process Management](02-ProcessManagement.md)
- [Nächste: DLL Loading →](04-DLLModuleLoading.md)
- [Miscellaneous](10-Miscellaneous.md)

---

**Kategorie**: GUI/TUI Operations (IDs 301-326)  
**Letztes Update**: 2026-04-23
