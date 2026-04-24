def require_tui():syscall(301)

def unlock_tui():syscall(302)

def printl(text):syscall(304,text)

pid = ret

require_tui()

printl(f"Running process {pid} with x=12 and i=22")

unlock_tui()