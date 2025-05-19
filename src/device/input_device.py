################################################################################
from abc import ABC
from queue import Queue, Empty
from typing import Optional

################################################################################
class InputDevice(ABC):

    def __init__(self):
        self.maxsize: int = -1
        self.queue: Queue = Queue(maxsize=self.maxsize)

    # --------------------------------------------------------------------------------
    def write(self, input_: str):
        if not self.queue.qsize() < self.maxsize:
            self.queue.put(input_)

    # --------------------------------------------------------------------------------
    def read(self, block: bool = False) -> Optional[str]:
        try:
            return self.queue.get(block=block)
        except Empty:
            return None


    def clear(self):
        with self.queue.mutex:
            self.queue.queue.clear()
