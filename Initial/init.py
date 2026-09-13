#
# Needs Export
#

def require_tui():syscall(301) # pyright: ignore[reportUndefinedVariable]

def unlock_tui():syscall(302) # pyright: ignore[reportUndefinedVariable]

def printl(text):syscall(304,text) # pyright: ignore[reportUndefinedVariable]

def read_c() -> str:
    return syscall(321) # pyright: ignore[reportUndefinedVariable]

def read_l() -> str:
    return syscall(322) # pyright: ignore[reportUndefinedVariable]

def sleep(ms): syscall(909, ms) # pyright: ignore[reportUndefinedVariable]

pid = ret # pyright: ignore[reportUndefinedVariable]

#
# Init Process
#

require_tui()

printl(f"Running process {pid} with x=12 and i=22")

unlock_tui()

sleep(10)

for i in range(10):
    require_tui()
    printl(f"PID: {pid}I: {i};Hello")
    unlock_tui()
require_tui()
printl(f"Test Hello")
unlock_tui()

require_tui()
while True:
    line = read_l()
    if line == "sh" or line == "shutdown":
        break
    else:
        printl(line)


unlock_tui()
syscall(400)
#4i  82ujkJHKGFGJHGJHGJHG