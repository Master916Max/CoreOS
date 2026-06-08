from typing import Any
from random import randint

class Cell:
    def __init__(self, owner,content:Any):
        self.owner = owner
        self.content = content
    def __rpr__(self):
        return f"Cell(owner={self.owner}, content={self.content})"
    def __str__(self):
        return self.__rpr__()

class MemoryManager:
    def __init__(self):
        self.memory = [Cell(None,None)]*1024*8

        # Pointers of starts of free spaces in memory
        self.empty_pointers = [0]

        self.data_pointers = []

        kernel_pointer = randint(0,1024*4)

        self.gst_ptr = kernel_pointer

        for i in range(1024*2):
            self.memory[self.gst_ptr + i] = Cell("syscall_mgr",None)
            self.data_pointers.append(self.gst_ptr + i)
        
    def malloc(self,owner,size):
        if len(self.empty_pointers) == 0:
            raise MemoryError("Out of Memory")
        # Get the next free space in memory

        found_space = False
        iteration = 1
        mem_pointer = None

        while not found_space:
            next_free_space = self.empty_pointers[-iteration]
            for i in range(size):
                if i + next_free_space in self.data_pointers:
                    continue
                if i + next_free_space >= len(self.memory):
                    raise MemoryError("Out of Memory")
            
            found_space = True
            mem_pointer = next_free_space
        
        # Mark the space as used
        for i in range(size):
            self.memory[mem_pointer + i] = Cell(owner,None)
            self.data_pointers.append(mem_pointer + i)
        # Remove the pointer from the empty pointers list
        self.empty_pointers.remove(mem_pointer)
        return mem_pointer

    def free(self,owner,pointer,size):
        for i in range(size):
            if self.memory[pointer + i].owner != owner:
                raise MemoryError("Memory Corruption Detected")
            self.memory[pointer + i] = Cell(None,None)
            self.data_pointers.remove(pointer + i)
        self.empty_pointers.append(pointer)
    
    def read(self,owner,pointer):
        if self.memory[pointer].owner != owner:
            raise MemoryError("Memory Corruption Detected")
        return self.memory[pointer].content
    
    def write(self,owner,pointer,data):
        if self.memory[pointer].owner != owner:
            raise MemoryError("Memory Corruption Detected")
        self.memory[pointer].content = data