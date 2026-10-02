from __future__ import annotations

import os
import signal
import time
from multiprocessing import Process as MpProcess

from ..common import *
from .process_u import Communication, MessageTypes, PipeMessage
from .process_u import Process as pu


class _Process:
    """Bookkeeping for one spawned OS process."""
    def __init__(self, pid: int, coms: Communication, mp_proc: MpProcess) -> None:
        self.pid = pid
        self.coms = coms
        self.mp_proc = mp_proc
        self.state = "created"
        self.syscall_to_send: dict = {}


class ProcessManager:
    def __init__(self, route_msg: RouteFNCType) -> None:
        self.route_msg = route_msg
        self.msg_queue: list[Message] = []
        self.processes: dict[int, _Process] = {}
        self.next_pid_to_run = 1
        self.next_pid = 1
        self.logger = Logger(Module.PROCESS)

        self.register_ipc()

    def register_ipc(self) -> None:
        reg_msg = Message()
        reg_msg.set_header(Module.PROCESS, Module.IPC, False)
        reg_msg.set_body({
            "action": "register",
            "module": Module.PROCESS,
            "queue": self.msg_queue,
        })
        self.route_msg(reg_msg)

    def spawn_process(self, code: str = "") -> int:
        pid = self.next_pid
        self.next_pid += 1

        coms = Communication()
        mp_proc = MpProcess(
            target=pu(code, pid, coms.get_p_side()).run,
            name=f"proc-{pid}",
            daemon=True,
        )
        mp_proc.start()

        self.processes[pid] = _Process(pid, coms, mp_proc)
        self.logger.log(0, f"Process spawned: pid={pid}")
        return pid

    def kill_process(self, pid: int) -> bool:
        worker = self.processes.get(pid)
        if worker is None:
            self.logger.log(2, f"kill_process: unknown pid {pid}")
            return False

        worker.coms.send_msg(MessageTypes.EXIT)
        worker.mp_proc.join(timeout=2)
        if worker.mp_proc.is_alive():
            worker.mp_proc.terminate()
            worker.mp_proc.join(timeout=1)
        worker.coms.close()

        exitcode = worker.mp_proc.exitcode
        del self.processes[pid]
        self.logger.log(0, f"Process killed: pid={pid}, exitcode={exitcode}")
        return True

    def handle_msgs(self) -> None:
        # Iterate over a snapshot, not self.msg_queue directly: every
        # branch below removes the handled message right after dealing
        # with it, so mutating the live list mid-iteration would skip
        # entries. (This is the bug that's still open in IPC.handle_msgs -
        # fixed here on purpose.)
        for msg in self.msg_queue:
            body = msg.get_body()
            action = body.get("action", None)

            if action == "create":
                pid = self.spawn_process(body.get("code", ""))
                self.route_msg(msg.answer({"action": "return", "pid": pid}))
            elif action == "kill":
                ok = self.kill_process(body.get("pid", -1))
                self.route_msg(msg.answer({"action": "return", "ok": ok}))
            elif action == "set_next":
                self.next_pid_to_run = body.get("next_pid", self.next_pid_to_run)
                self.route_msg(msg.answer({"action": "return", "next_pid": self.next_pid_to_run}))
            elif action == "syscall_ret":
                pid = body.get("pid", -1)
                process = self.processes.get(pid)
                if process is None:
                    self.logger.log(2, f"syscall_ret: unknown pid {pid}")
                    self.route_msg(msg.answer({
                        "action": "return",
                        "error": Error(
                            ErrorType.ProcessError,
                            ProcessErrorCode.UnknownPID,
                            f"Unknown pid: {pid}",
                        ),
                    }))
                else:
                    process.syscall_to_send =  body.get("args", ())
                    if msg.answer_required:
                        self.route_msg(msg.answer({"action": "return", "ok": True}))
            else:
                self.route_msg(msg.answer({
                    "action": "return",
                    "error": Error(
                        ErrorType.ProcessError,
                        ProcessErrorCode.UnsupportedAction,
                        f"Unsupported action: {action!r}",
                    ),
                }))

            self.msg_queue.remove(msg)

    def execute(self) -> None:
        process = self.processes.get(self.next_pid_to_run)
        if process is None:
            self.logger.log(2, f"execute: unknown pid {self.next_pid_to_run}")
            return
        
        match process.state:
            case "created":
                process.mp_proc.start()
                process.coms.send_msg(MessageTypes.CONTINUE)
                process.state = "running"
            case "running":
                os.kill(process.mp_proc.pid, signal.SIGCONT)
            case "syscall":
                if process.syscall_to_send:
                    process.coms.send_msg(MessageTypes.SYSCALL, **process.syscall_to_send)
                    process.syscall_to_send = {}
                else:
                    self.logger.log(2, f"execute: pid {self.next_pid_to_run} has no syscall to return")
                    return
            case "terminated":
                self.logger.log(2, f"execute: pid {self.next_pid_to_run} is terminated")
                return
            case _:
                self.logger.log(2, f"execute: pid {self.next_pid_to_run} has unknown state {process.state}")
                return
        
        msg: dict | None = process.coms.get_msg(timeout=0.1)
        os.kill(process.mp_proc.pid, signal.SIDSTOP)

        if msg:
            msg_type = msg.get("type", MessageTypes.EXIT)
            if msg_type == MessageTypes.EXIT:
                process.state = "terminated"
                self.logger.log(0, f"Process {self.next_pid_to_run} exited")
            elif msg_type == MessageTypes.SYSCALL:
                process.state = "syscall"
                args: list= msg.get("args", ())
                msg_s = Message()
                msg_s.set_header(Module.PROCESS, Module.SYSCALLMANAGER, True)
                msg_s.set_body({
                    "action": "syscall",
                    "pid" : process.pid,
                    "sid" : args[0],
                    "sargs": args})
                self.logger.log(0, f"Process {self.next_pid_to_run} made a syscall with this body: ('action': 'syscall', 'pid' : {process.pid}, 'sid' : {args[0]}, 'sargs': {args})")
            else:
                self.logger.log(2, f"execute: pid {self.next_pid_to_run} sent unknown message type {msg_type}")
                process.state = "terminated"
        else:
            pass

    def loop(self) -> None:
        self.handle_msgs()

        self.execute()

    def shutdown(self) -> Logger:
        for pid in list(self.workers.keys()):
            self.kill_process(pid)
        return self.logger