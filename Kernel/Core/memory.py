from types import FunctionType
from typing import Any
from random import randint

from ..IPC.common import Message, Module

from .logger import Logger


class Cell:
    def __init__(self, owner,content:Any):
        self.owner = owner
        self.content = content
    def __rpr__(self):
        return f"Cell(owner={self.owner}, content={self.content})"
    def __str__(self):
        return self.__rpr__()

class MemoryManager:
    def __init__(self, rout_msg:FunctionType):
        self.logger = Logger()
        self.memory = [
            Cell(None, None)
            for _ in range(1024 * 8)
        ]

        self.msg_rout = rout_msg
        self.msg_queue = []

        # Pointers of starts of free spaces in memory
        self.empty_pointers = [0]
        self.data_pointers = []

        kernel_pointer = randint(0,1024*4)

        self.gst_ptr = kernel_pointer

        for i in range(1024*2):
            self.memory[self.gst_ptr + i] = Cell("syscall_mgr",None)
            self.data_pointers.append(self.gst_ptr + i)

        register_msg = Message()
        register_msg.set_header(Module.MEMORY,Module.IPC,False)
        register_msg.set_body({
            "action": "register",
            "module": Module.MEMORY,
            "queue": self.msg_queue
        })
        self.msg_rout(register_msg)
        
    def malloc(self,owner,size):
        self.logger.log(0,f"Owner:{owner} allocated: {size}")
        if len(self.empty_pointers) == 0:
            raise MemoryError("Out of Memory")
        # Get the next free space in memory

        found_space = False
        iteration = 1
        mem_pointer = 0

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
        self.logger.log(0,f"Owner:{owner} freed: {size} at: {pointer}")
        for i in range(size):
            if self.memory[pointer + i].owner != owner:
                raise MemoryError("Memory Corruption Detected")
            self.memory[pointer + i] = Cell(None,None)
            self.data_pointers.remove(pointer + i)
        self.empty_pointers.append(pointer)
    
    def read(self,owner,pointer):
        self.logger.log(0,f"Owner:{owner} read: {pointer}")
        if self.memory[pointer].owner != owner:
            raise MemoryError("Memory Corruption Detected")
        return self.memory[pointer].content
    
    def write(self,owner,pointer,data):
        self.logger.log(0,f"Owner:{owner} wrote: {pointer} at: {data}")
        if self.memory[pointer].owner != owner:
            raise MemoryError("Memory Corruption Detected")
        self.memory[pointer].content = data
    
    def shutdown(self):
        self.data_pointers = []
        self.empty_pointers = []
        self.memory = []
        
        return self.logger

    def handle_messages(self):
        while len(self.msg_queue) > 0:
            msg = self.msg_queue.pop(0)
            if msg.to == Module.MEMORY:
                if msg.content["action"] == "malloc":
                    pointer = self.malloc(msg.content["owner"],msg.content["size"])
                    answer_msg = msg.answer({"pointer": pointer})
                    self.msg_rout(answer_msg)
                elif msg.content["action"] == "free":
                    self.free(msg.content["owner"],msg.content["pointer"],msg.content["size"])
                elif msg.content["action"] == "read":
                    data = self.read(msg.content["owner"],msg.content["pointer"])
                    answer_msg = msg.answer({"data": data})
                    self.msg_rout(answer_msg)
                elif msg.content["action"] == "write":
                    self.write(msg.content["owner"],msg.content["pointer"],msg.content["data"])