
def open(path, mode) -> int:
    syscall(1,path,mode)
    return ret

def require_tui():
    syscall(301)

def unlock_tui():
    syscall(302)

def print(text):
    syscall(304,text)
