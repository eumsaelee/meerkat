import threading
from abc import ABC, abstractmethod
from typing import Callable, Any

import numpy as np

from meerkat.video.readers import Reader
from meerkat.video.buffers import Buffer


# --- Interface ---


class Updater(ABC, threading.Thread):
    def __init__(self, reader: Reader, buffer: Buffer):
        super().__init__()
        self._reader = reader
        self._buffer = buffer
        self._halt = False
        self._lock = threading.Lock()

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def read(self, timeout: float=None) -> Any:
        pass


# --- Class ---


class FrameUpdater(Updater):
    def __init__(self,
                 reader: Reader,
                 buffer: Buffer,
                 encode: Callable[[np.ndarray], Any]=None):
        super().__init__(reader, buffer)
        self._encode = encode

    def run(self):
        while not self._halt:
            frame = self._reader.read()
            self._buffer.put(frame)

    def stop(self, is_released=False):
        self._halt = True
        if is_released:
            self._reader.release()

    def read(self, timeout: float=None) -> Any:
        frame = self._buffer.get(timeout)
        if self._encode:
            return self._encode(frame)
        return frame

    def __repr__(self) -> str:
        return ('FrameUpdater('
                f'reader={self._reader!r}, '
                f'buffer={self._buffer!r}, '
                f'encode={self._encode!r})')
