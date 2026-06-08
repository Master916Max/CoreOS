# GUI/TUI Operations Syscalls


### 350. `Is_GUI_Avaliable` - 

**Parameter**: `(timeout_ms: int=0)`  
**Rückgabe**: `int (0=unavaliable,1=avaliable)`  

Sperrt Output für diesen Prozess. Andere Prozesse warten.

**Beispiel**:
```python
syscall(301)
if ret == 1:
    print("GUI-Mode Avaliable")
```

---

### 351. `Switch-To-GUI-Mode` - 

**Parameter**: `(timeout_ms: int=0)`  
**Rückgabe**: `int (0=sucess)`  

Sperrt Output für diesen Prozess. Andere Prozesse warten.

**Beispiel**:
```python
syscall(301)
if ret != 0:
    print("GUI-Mode switch Failed")
```

---