from types import FunctionType
from typing import Any

from ..IPC.common import Message, Module
from .erros import IPCErrorCode, MemoryErrorCode, ErrorType, Error,Return

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
    def __init__(self, rout_msg: FunctionType) -> None:
        self.logger = Logger()

        self.memory = [
            Cell(None, None)
            for _ in range(1024 * 8)
        ]

        self.msg_rout = rout_msg
        self.msg_queue: list[Message] = []

        # -------------------------------------------------
        # Memory layout
        # -------------------------------------------------

        self.memory_size = len(self.memory)

        # Track allocated/reserved cells
        self.data_pointers = set()
        
        # -------------------------------------------------
        # Free memory blocks
        #
        # (start, size)
        # -------------------------------------------------
        self.empty_pointers = []
        self.empty_pointers.append((0, self.memory_size))


        # Register memory manager
        register_msg = Message()
        register_msg.set_header(
            Module.MEMORY,
            Module.IPC,
            False
        )
        register_msg.set_body({
            "action": "register",
            "module": Module.MEMORY,
            "queue": self.msg_queue
            })

        self.msg_rout(register_msg)

        self.action = {
            "kalloc" : self.malloc,
            "read"   : self.read,
            "write"  : self.write,
            "free"   : self.free
        }

    def malloc(self, owner, size) -> Return:
        self.logger.log(0,f"Owner:{owner} allocated: {size}")

        if size <= 0:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.InvalidMemorySize,"Size can't be 0 long!"))

        if owner == None:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.InvalidMemorySize,"The Owner can't be none!"))
        # Find a free block large enough
        for index, (start, block_size) in enumerate(self.empty_pointers):
            if block_size < size:
                continue

            pointer = start
            # Mark memory as allocated
            for i in range(size):
                address = pointer + i
                self.memory[address] = Cell(owner,None)
                self.data_pointers.add(address)

            # -------------------------------------------------
            # Update free block
            # -------------------------------------------------
            remaining = block_size - size

            if remaining == 0:
                # The entire block was used
                self.empty_pointers.pop(index)
            else:
                # Keep the remaining part
                self.empty_pointers[index] = (start + size,remaining)

            return Return(pointer)

        # No block was large enough
        return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.OutOfMemory,"Out off Memory!"))

    def free(self, owner, pointer, size) -> Return:
        self.logger.log(0,f"Owner:{owner} freed: {size} at: {pointer}")

        if size <= 0:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.InvalidMemorySize,"Size can't be 0 long!"))

        if pointer < 0:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.InvalidMemorySize,"Pointer can't be less then 0!"))

        if pointer + size > self.memory_size:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.InvalidMemorySize,"Memory range is out of bounds"))

        if owner == None:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.InvalidMemorySize,"The Owner can't be none!"))
        # -------------------------------------------------
        # Verify ownership BEFORE changing anything
        # -------------------------------------------------

        for i in range(size):
            address = pointer + i

            if address not in self.data_pointers:
                return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.MemoryCorruptionDetected,"Memory Corruption Detected"))

            if self.memory[address].owner != owner:
                return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.MemoryCorruptionDetected,"Memory Corruption Detected"))

        # -------------------------------------------------
        # Free memory
        # -------------------------------------------------

        for i in range(size):
            address = pointer + i
            self.memory[address] = Cell(None,None)
            self.data_pointers.remove(address)

        # Add newly freed block
        self.empty_pointers.append((pointer, size))

        # Merge adjacent blocks
        self._merge_free_blocks()
        return Return(True)

    def _merge_free_blocks(self):
        """
        Merge neighbouring free memory blocks.

        Example:

        (0, 10)
        (10, 20)

        becomes:

        (0, 30)
        """

        if not self.empty_pointers:
            return

        # Sort by memory address
        self.empty_pointers.sort(key=lambda block: block[0])

        merged = []

        for start, size in self.empty_pointers:

            if not merged:
                merged.append((start, size))
                continue

            previous_start, previous_size = merged[-1]
            previous_end = ( previous_start + previous_size)
            
            # Blocks are directly adjacent
            if previous_end == start:
                merged[-1] = (previous_start,previous_size + size)
            else:
                merged.append((start, size))

        self.empty_pointers = merged

    def read(self, owner, pointer) -> Return:

        if owner == None:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.InvalidMemorySize,"The Owner can't be none!"))
        
        self.logger.log(0,f"Owner:{owner} read: {pointer}")

        if pointer < 0 or pointer >= self.memory_size:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.InvalidMemorySize,"Invalid memory pointer"))

        if self.memory[pointer].owner != owner:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.MemoryCorruptionDetected,"Memory Corruption Detected"))

        return Return(self.memory[pointer].content)

    def write(self, owner, pointer, data) -> Return:
        self.logger.log(0,f"Owner:{owner} wrote: {pointer} at: {data}")

        if owner == None:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.InvalidMemorySize,"The Owner can't be none!"))

        if pointer < 0 or pointer >= self.memory_size:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.InvalidMemorySize,"Invalid memory pointer"))

        if self.memory[pointer].owner != owner:
            return Return(False,Error(ErrorType.MemoryError,MemoryErrorCode.MemoryCorruptionDetected,"Memory Corruption Detected"))

        self.memory[pointer].content = data
        return Return(True)

    def shutdown(self) -> Logger:
        self.data_pointers = set()
        self.empty_pointers = []
        self.memory = []

        return self.logger

    def handle_msgs(self) -> None:
        for msg in self.msg_queue:
            body = msg.get_body()
            action = body.get("action", None)

            if action in self.action:
                match action:
                    case "kalloc":
                        self.msg_rout(msg.answer({
                            "action":"return",
                            "return":self.malloc(body.get("owner", None),body.get("size", 0))
                        }))
                        break
                    case "free":
                        self.msg_rout(msg.answer({
                            "action":"return",
                            "return":self.free(body.get("owner", None),body.get("pointer", 0),body.get("size", 0))
                        }))
                        break
                    case "read":
                        self.msg_rout(msg.answer({
                            "action":"return",
                            "return":self.read(body.get("owner", None),body.get("pointer", 0))
                        }))
                        break
                    case "write":
                        self.msg_rout(msg.answer({
                            "action":"return",
                            "return":self.write(body.get("owner", None),body.get("pointer", 0),body.get("data", None))
                        }))
                        break
            else:
                msg.answer(
                    {
                        "action":"return",
                        "error" : ErrorType.IPCError,
                        "code"  : IPCErrorCode.InvalidMSGBody
                    }
                )

