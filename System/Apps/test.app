#Type=console
#SystemDLL=system

def load_library(name): 
    syscall(401,name)
    return ret

hnd = load_library(system.dll)

def load_function(hnd,idx):
    return read_mem(hnd+1+idx)

shutdown = load_function(hnd,1017)

shutdown()