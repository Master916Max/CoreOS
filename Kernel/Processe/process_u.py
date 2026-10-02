from __future__ import annotations

from enum import Enum
from multiprocessing import Pipe
from multiprocessing.connection import Connection


class MessageTypes(Enum):
    CONTINUE = "continue"
    SYSCALL = "syscall"
    EXIT = "exit"


class PipeMessage:
    def __init__(self, sender: int | str, receiver: int | str, message: dict) -> None:
        self.sender = sender
        self.receiver = receiver
        self.message = message

    def __repr__(self) -> str:
        return f"PipeMessage(from={self.sender!r}, to={self.receiver!r}, msg={self.message!r})"


class Communication:
    """
    Wraps one end of a duplex multiprocessing Pipe.

    Create without arguments on the kernel side - this opens a fresh pipe
    pair. Call get_p_side() to obtain the matching Communication for the
    child process and pass that into the child's Process.
    """

    def __init__(self, user_side: bool = False, pipe: Connection | None = None) -> None:
        self._user_side = user_side
        if not user_side:
            self._kernel_end, self._child_end = Pipe(duplex=True)
            self.pipe: Connection = self._kernel_end
        else:
            if pipe is None:
                raise ValueError("user_side Communication requires an explicit pipe")
            self.pipe = pipe

    def get_p_side(self) -> Communication:
        if self._user_side:
            raise RuntimeError(
                "get_p_side() can only be called on the kernel-side Communication"
            )
        return Communication(True, self._child_end)

    def send_msg(self, msg_type: MessageTypes, *args) -> bool:
        """Returns True if the message was sent, False if the peer is gone."""
        try:
            self.pipe.send(PipeMessage("Kernel", 1, {"type": msg_type, "args": args}))
            return True
        except (BrokenPipeError, EOFError, OSError):
            return False

    def get_msg(self, timeout: float | None = 0) -> dict | None:
        """
        timeout=0     -> return immediately (non-blocking poll)
        timeout=N     -> wait up to N seconds
        timeout=None  -> block at the OS level until a message arrives
        """
        try:
            if not self.pipe.poll(timeout):
                return None
            msg: PipeMessage = self.pipe.recv()
            return msg.message
        except (BrokenPipeError, EOFError, OSError):
            return None

    def close(self) -> None:
        try:
            self.pipe.close()
        except OSError:
            pass


class Process:
    def __init__(self, code, pid, coms: Communication) -> None:
        self.code = code
        self.pid = pid
        self.coms = coms
        self.running = False

    def can_execute(self, timeout: float | None = None) -> bool:
        """
        Waits (blocking by default) for the next message and decides
        whether the process should keep running.
        """
        msg = self.coms.get_msg(timeout=timeout)
        if msg is None:
            return False

        msg_type = msg.get("type", MessageTypes.EXIT)
        if msg_type == MessageTypes.EXIT:
            return False
        if msg_type == MessageTypes.SYSCALL:
            self.handle_syscall(*msg.get("args", ()))
            return True
        return msg_type == MessageTypes.CONTINUE

    def run(self) -> None:
        self.running = True
        while self.running:
            self.running = self.can_execute(timeout=None)
        self.coms.close()

    def handle_syscall(self, *args) -> object:
        return None