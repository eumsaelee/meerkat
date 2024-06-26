"""
    Exceptions:
        - BufferSizeError

    Interfaces:
        - Buffer

    Classes:
        - FrameBuffer(Buffer)
        - AsyncFrameBuffer(Buffer)
"""


import time
import asyncio
import threading
from abc import ABC, abstractmethod

import numpy as np

from meerkat.common import CommonException


class BufferSizeError(CommonException): pass


class Buffer(ABC):
    """ Interface """

    def __init__(self, size: int=1):
        self._size = size

    @property
    @abstractmethod
    def size(self) -> int:
        pass

    @size.setter
    @abstractmethod
    def size(self, value: int):
        pass

    @abstractmethod
    def _inspect_size(self, value: int) -> int:
        pass

    @abstractmethod
    def put(self, frame: np.ndarray):
        pass

    @abstractmethod
    def get(self, timeout: float=30.0) -> np.ndarray:
        pass


class FrameBuffer(Buffer):
    """  """

    def __init__(self, size: int=1):
        super().__init__(self._inspect_size(size))
        self._frames = []
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)

    @property
    def size(self) -> int:
        with self._lock:
            return self._size

    @size.setter
    def size(self, value: int):
        new_size = self._inspect_size(value)
        with self._lock:
            if new_size < self._size:
                self._frames = self._frames[-new_size:]
            self._size = new_size

    def _inspect_size(self, value: int) -> int:
        if isinstance(value, int) and value > 0:
            return value
        raise BufferSizeError(
            f'The size must be a positive integer, not {value!r}.')

    def put(self, frame: np.ndarray):
        with self._lock:
            if len(self._frames) >= self._size:
                self._frames.pop(0)
            self._frames.append(frame)
            self._not_empty.notify()

    def get(self, timeout: float=30.0) -> np.ndarray:
        with self._not_empty:
            t0 = time.time()
            while not self._frames:
                t1 = time.time()
                remainder = timeout - (t1 - t0)
                if remainder <= 0:
                    raise TimeoutError(
                        'Timeout within recheck.')
                if not self._not_empty.wait(remainder):
                    raise TimeoutError(
                        'Timeout within wait.')
            frame = self._frames.pop(0)
            return frame

    def __len__(self) -> int:
        return len(self._frames)

    def __repr__(self) -> str:
        return f'FrameBuffer(size={self._size!r})'


class AsyncFrameBuffer(Buffer):
    """  """

    def __init__(self, size: int=1):
        super().__init__(self._inspect_size(size))
        self._frames = []
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Condition(self._lock)

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    async def size(self, value: int):
        new_size = self._inspect_size(value)
        async with self._lock:
            if new_size < self._size:
                self._frames = self._frames[-new_size:]
            self._size = new_size

    def _inspect_size(self, value: int) -> int:
        if isinstance(value, int) and value > 0:
            return value
        raise BufferSizeError(
            f'The size must be a positive integer, not {value!r}.')

    async def put(self, frame: np.ndarray):
        async with self._lock:
            if len(self._frames) >= self._size:
                self._frames.pop(0)
            self._frames.append(frame)
            self._not_empty.notify()

    async def get(self, timeout: float=30.0) -> np.ndarray:
        async with self._not_empty:
            t0 = asyncio.get_running_loop().time()
            while not self._frames:
                t1 = asyncio.get_running_loop().time()
                remainder = timeout - (t1 - t0)
                if remainder <= 0:
                    raise TimeoutError(
                        'Timeout within recheck.')
                if not await self._not_empty.wait(remainder):
                    raise TimeoutError(
                        'Timeout within wait.')
            frame = self._frames.pop(0)
            return frame

    def __len__(self) -> int:
        return len(self._frames)

    def __repr__(self) -> str:
        return f'AsyncFrameBuffer(size={self._size!r})'
