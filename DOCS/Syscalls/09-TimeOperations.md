# Time Operations Syscalls

**Kategorie-ID**: 901-910  
**Scope**: Zeit, Uhr, Timer, Verzögerungen

[← Übersicht](README.md) | [← Zurück: Threading](08-Threading.md) | [Nächste: Miscellaneous →](10-Miscellaneous.md)

---

## Übersicht

Zeit- und Timer-Verwaltung.

| ID | Syscall | Beschreibung |
|---|---------|------------|
| 901 | `time` | Aktuelle Unix-Zeit |
| 902 | `gettimeofday` | Zeit mit Microsekunden |
| 903 | `settimeofday` | Zeit setzen |
| 904 | `clock_gettime` | Verschiedene Clocks |
| 905 | `clock_settime` | Clock setzen |
| 906 | `timer_create` | Timer erstellen |
| 907 | `timer_settime` | Timer konfigurieren |
| 908 | `timer_delete` | Timer löschen |
| 909 | `sleep` | Schlafen (Sekunden) |
| 910 | `usleep` | Schlafen (Microsekunden) |

---

## Zeit abrufen (901-905)

### 901. `time` - Sekunden seit Epoch

**Parameter**: `()`  
**Rückgabe**: `int (seconds)`

**Beispiel**:
```python
now = syscall(901)
print(f"Zeit: {now}")  # 1703001234
```

---

### 902. `gettimeofday` - Präzise Zeit

**Parameter**: `()`  
**Rückgabe**: `dict ({sec, usec})`

**Beispiel**:
```python
time_info = syscall(902)
print(f"Zeit: {time_info['sec']}.{time_info['usec']:06d}")
```

---

### 903. `settimeofday` - Zeit ändern

**Parameter**: `(sec: int, usec: int)`  
**Rückgabe**: `int (0=success)`

**Beispiel**:
```python
# Systemzeit setzen (erfordert Rechte)
result = syscall(903, 1700000000, 0)
```

---

### 904-905. Verschiedene Clocks

**Beispiel**:
```python
# CLOCK_REALTIME (0)
time_real = syscall(904, 0)
print(f"Real: {time_real['sec']}.{time_real['nsec']}")

# CLOCK_MONOTONIC (1) - läuft immer vorwärts
time_mono = syscall(904, 1)

# Clock setzen (nur bestimmte Clocks)
syscall(905, 0, 1700000000, 0)
```

---

## Timer (906-908)

### 906-908. Timer-Verwaltung

**Beispiel**:
```python
def timer_callback(timer_id):
    print(f"Timer {timer_id} abgelaufen!")

# Timer erstellen
timer_id = syscall(906, 0, timer_callback)  # clock=0 (REALTIME)

# Timer konfigurieren (initial_ms, interval_ms)
syscall(907, timer_id, 1000, 500)  # 1s später, dann alle 500ms

# Timer löschen
syscall(908, timer_id)
```

---

## Verzögerungen (909-910)

### 909-910. Sleep

**Beispiel**:
```python
# 5 Sekunden schlafen
syscall(909, 5)

# 500 Millisekunden
syscall(910, 500000)

# 100 Nanosekunden (praktisch 0)
syscall(910, 100)
```

---

## Häufige Muster

### Einfacher Countdown-Timer

```python
def countdown(seconds):
    for i in range(seconds, 0, -1):
        syscall(301)  # acquire lock
        syscall(304, f"Countdown: {i}s")
        syscall(302)  # release lock
        
        syscall(909, 1)  # sleep 1s
```

### Performance-Messung

```python
def measure_time(func, args):
    start = syscall(902)
    
    func(*args)
    
    end = syscall(902)
    
    elapsed = (end['sec'] - start['sec']) + \
              (end['usec'] - start['usec']) / 1000000
    
    return elapsed
```

### Periodischer Task

```python
def periodic_task(interval_ms, callback):
    timer = syscall(906, 0, None)  # clock=REALTIME
    syscall(907, timer, interval_ms, interval_ms)
    
    while True:
        callback()
        syscall(910, interval_ms * 1000)
```

### Timeout-Protection

```python
def call_with_timeout(func, timeout_sec):
    start = syscall(902)
    
    while True:
        current = syscall(902)
        elapsed = current['sec'] - start['sec']
        
        if elapsed >= timeout_sec:
            return None
        
        try:
            result = func()
            return result
        except:
            syscall(910, 100000)  # 100ms
```

---

## Verwandte Kategorien

- [← Zurück: Threading](08-Threading.md)
- [Nächste: Miscellaneous →](10-Miscellaneous.md)
- [Process Management](02-ProcessManagement.md)

---

**Kategorie**: Time Operations (IDs 901-910)  
**Letztes Update**: 2026-04-23
