from multiprocessing import Process

from ..IPC.common import RouteFNCType,Module,Message
from .process_u import Process as pu
from .process_u import Communication

class ProcessManager:
    def __init__(self, route_msg) -> None:
        pass


Process(target=pu, name="test_pid",daemon=True).start()