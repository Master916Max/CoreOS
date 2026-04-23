# DLL/Module Loading Syscalls

**Kategorie-ID**: 401-415  
**Scope**: Dynamische Bibliotheken und Module

[← Übersicht](README.md) | [← Zurück: GUI/TUI](03-GUITUIOperations.md) | [Nächste: Memory →](05-MemoryManagement.md)

---

## Übersicht

Dynamisches Laden von Bibliotheken (DLL/SO) und Symbol-Auflösung. Windows-Style Modulverwaltung.

| ID | Syscall | Beschreibung |
|---|---------|------------|
| 401 | `load_library` | Bibliothek laden |
| 402 | `load_dll` | DLL laden (Alias zu load_library) |
| 403 | `unload_library` | Bibliothek entladen |
| 404 | `get_module_handle` | Handle zu geladener Bibliothek |
| 405 | `reload_module` | Modul neu laden |
| 406 | `get_dll_exports` | Exportierte Funktionen |
| 407 | `get_dll_imports` | Importierte Funktionen |
| 408 | `get_dll_info` | Bibliothek-Informationen |
| 409 | `get_dll_version` | Versions-String |
| 410 | `get_procedure_address` | Funktion abrufen |
| 411 | `get_symbol_address` | Symbol-Adresse |
| 412 | `list_loaded_modules` | Alle geladenen Module |
| 413 | `link_module` | Module verknüpfen |
| 414 | `unlink_module` | Verknüpfung trennen |
| 415 | `get_module_base` | Basis-Adresse |

---

## Detaillierte Beschreibungen

### 401-402. `load_library` / `load_dll` - Bibliothek laden

**Parameter**: `(path: str)`  
**Rückgabe**: `int (handle)`  
**Fehler**: `FILE_NOT_FOUND`, `INVALID_DLL`, `LOAD_ERROR`

**Beispiel**:
```python
# Windows-Pfad
handle = syscall(401, "C:\\libs\\mylib.dll")
if handle > 0:
    print(f"Bibliothek geladen: Handle={handle}")
else:
    print(f"Fehler: {handle}")

# Linux-Style (auch möglich)
handle = syscall(402, "/usr/lib/libmath.so")

# Relative Pfade
handle = syscall(401, "modules\\helper.dll")
```

---

### 403. `unload_library` - Bibliothek entladen

**Parameter**: `(handle: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `INVALID_HANDLE`, `IN_USE`

**Beispiel**:
```python
handle = syscall(401, "C:\\libs\\mylib.dll")
# ... Funktionen nutzen ...
result = syscall(403, handle)
if result == 0:
    print("Bibliothek entladen")
```

---

### 404. `get_module_handle` - Handle abrufen

**Parameter**: `(name: str)`  
**Rückgabe**: `int (handle)`  
**Fehler**: `MODULE_NOT_FOUND`

**Beispiel**:
```python
# Handle zu bereits geladenem Modul
handle = syscall(404, "mylib")
if handle > 0:
    print(f"Handle: {handle}")
```

---

### 405. `reload_module` - Modul neu laden

**Parameter**: `(handle: int)`  
**Rückgabe**: `int (0=success)`  
**Fehler**: `INVALID_HANDLE`, `LOAD_ERROR`

**Beispiel**:
```python
handle = syscall(401, "C:\\libs\\config.dll")
# ... Modul nutzen ...
# Nach Update neu laden
syscall(405, handle)
```

---

### 406-407. Exporte und Importe

**Parameter get_dll_exports**: `(handle: int)`  
**Parameter get_dll_imports**: `(handle: int)`  
**Rückgabe**: `list (names)`

**Beispiel**:
```python
handle = syscall(401, "C:\\libs\\math.dll")

# Exportierte Funktionen
exports = syscall(406, handle)
for func in exports:
    print(f"Export: {func}")
# Ausgabe: func_add, func_multiply, ...

# Importierte Funktionen
imports = syscall(407, handle)
for imp in imports:
    print(f"Import: {imp}")
```

---

### 408. `get_dll_info` - Bibliothek-Informationen

**Parameter**: `(handle: int)`  
**Rückgabe**: `dict (info)`

**Beispiel**:
```python
info = syscall(408, handle)
print(f"Name: {info['name']}")
print(f"Pfad: {info['path']}")
print(f"Größe: {info['size']}")
print(f"Exporte: {info['export_count']}")
print(f"Importe: {info['import_count']}")
```

---

### 409. `get_dll_version` - Version abrufen

**Parameter**: `(handle: int)`  
**Rückgabe**: `str (version)`

**Beispiel**:
```python
version = syscall(409, handle)
print(f"Version: {version}")  # "1.2.3"
```

---

### 410-411. Symbol/Prozedur-Adresse

**Parameter get_procedure_address**: `(handle: int, name: str)`  
**Parameter get_symbol_address**: `(handle: int, symbol: str)`  
**Rückgabe**: `int (address)`

**Beispiel**:
```python
# Funktion abrufen
handle = syscall(401, "C:\\libs\\calc.dll")

# Prozedur-Adresse
addr = syscall(410, handle, "add")
print(f"add() bei: {hex(addr)}")

# Symbol-Adresse
var_addr = syscall(411, handle, "PI")
print(f"PI bei: {hex(var_addr)}")
```

---

### 412. `list_loaded_modules` - Alle Module

**Parameter**: `()`  
**Rückgabe**: `list (modules)`

**Beispiel**:
```python
modules = syscall(412)
for mod in modules:
    print(f"{mod['name']}: {mod['path']}")
    print(f"  Handle: {mod['handle']}")
    print(f"  Exports: {mod['export_count']}")
```

---

### 413-414. Modul-Verknüpfung

**Parameter link_module**: `(handle1: int, handle2: int)`  
**Parameter unlink_module**: `(handle1: int, handle2: int)`  
**Rückgabe**: `int (0=success)`

**Beispiel**:
```python
# Zwei Module laden
h1 = syscall(401, "C:\\libs\\core.dll")
h2 = syscall(401, "C:\\libs\\plugin.dll")

# Verknüpfen
result = syscall(413, h1, h2)

# Später trennen
syscall(414, h1, h2)
```

---

### 415. `get_module_base` - Basis-Adresse

**Parameter**: `(handle: int)`  
**Rückgabe**: `int (base_address)`

**Beispiel**:
```python
base = syscall(415, handle)
print(f"Modul-Basis: {hex(base)}")
```

---

## Häufige Muster

### Sichere DLL-Nutzung

```python
def load_and_use_dll(path, func_name):
    handle = syscall(401, path)
    if handle < 0:
        return None
    
    try:
        addr = syscall(410, handle, func_name)
        if addr > 0:
            return addr
    finally:
        syscall(403, handle)  # immer entladen
    
    return None
```

### Plugin-System

```python
def load_plugins(plugin_dir):
    plugins = []
    
    # Verzeichnis auflisten
    dir_fd = syscall(13, plugin_dir)
    entries = syscall(14, dir_fd)
    syscall(15, dir_fd)
    
    for entry in entries:
        if entry['name'].endswith('.dll'):
            path = plugin_dir + "\\" + entry['name']
            handle = syscall(401, path)
            
            if handle > 0:
                info = syscall(408, handle)
                plugins.append({
                    'name': info['name'],
                    'handle': handle,
                    'exports': syscall(406, handle)
                })
    
    return plugins
```

### Versions-Check

```python
def check_module_version(path, min_version):
    handle = syscall(401, path)
    if handle < 0:
        return False
    
    version = syscall(409, handle)
    syscall(403, handle)
    
    # Vergleich: "1.2.3" > "1.0.0"
    return version >= min_version
```

---

## Verwandte Kategorien

- [← Zurück: GUI/TUI](03-GUITUIOperations.md)
- [Nächste: Memory Management →](05-MemoryManagement.md)
- [File I/O](01-FileIO.md)

---

**Kategorie**: DLL/Module Loading (IDs 401-415)  
**Letztes Update**: 2026-04-23
