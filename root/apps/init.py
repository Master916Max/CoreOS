#
# Needs Export
#

def require_tui():syscall(301)

def unlock_tui():syscall(302)

def print(text):syscall(303,text)

def printl(text):syscall(304,text)

def read_c() -> str:
    return syscall(321)

def read_l() -> str:
    return syscall(322)

def sleep(ms): syscall(909, ms)

pid = ret # pyright: ignore[reportUndefinedVariable]

#
# Init Process
#

require_tui()

printl(f"The Basic MOS-TUI-Shell has started")

unlock_tui()

sleep(10)

require_tui()

syscall(331) # pyright: ignore[reportUndefinedVariable]

while True:
    print(">")
    line = read_l()
    if line == "sh" or line == "shutdown":
        break
    else:
        printl(line)

syscall(332) # pyright: ignore[reportUndefinedVariable]

unlock_tui()
syscall(400) # pyright: ignore[reportUndefinedVariable]