"""
    Interfaces:
        - Capture

    Classes:
        - FrameCapture(Capture)
"""

import threading
from abc import ABC, abstractmethod
from typing import Callable, Any

import numpy as np

from meerkat.readers import Reader
from meerkat.buffers import Buffer


class Capture(ABC, threading.Thread):
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
    def read(self, timeout: float=30.0) -> Any:
        pass


class FrameCapture(Capture):

    def run(self):
        while not self._halt:
            frame = self._reader.read()
            self._buffer.put(frame)

    def stop(self, is_released=False):
        self._halt = True
        if is_released:
            self._reader.release()

    def read(self,
             timeout: float=30.0,
             encode: Callable[[np.ndarray], Any]=None) -> Any:
        frame = self._buffer.get(timeout)
        if encode:
            return encode(frame)
        return frame

    def __repr__(self) -> str:
        return ('FrameCapture('
                f'reader={self._reader!r}, '
                f'buffer={self._buffer!r})')
