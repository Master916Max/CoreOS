def require_tui():syscall(301)

def unlock_tui():syscall(302)

def printl(text):syscall(304,text)

def sleep(ms): syscall(909, ms)

pid = ret

require_tui()

printl(f"Running process {pid} with x=12 and i=22")

unlock_tui()

sleep(10)

for i in range(1):
    require_tui()
    printl(f"PID: {pid}I: {i};Hello")
    unlock_tui()
    #sleep(10)