import time


syscall(1, "std:out")

cmd_id = ret

if cmd_id == 0:
    print("ERROR")

syscall(3, (cmd_id, "Syscall Test successful!"))

syscall(1, "std:in")

cmd_in = ret

syscall(4, {"path":"First.py"})

syscall(2, cmd_in)

syscall(3, (cmd_id, f"You entered: {ret}"))

ret = 12
