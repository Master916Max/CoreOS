#
# Needs Export
#

syscall(141, "stfn.lib")

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
#4i  82ujkJHKGFGJHGJHGJHG