"""
    Interfaces:
        - Streamer
"""

import asyncio
import threading
import websockets
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Callable, Any

import numpy as np
from loguru import logger

from meerkat.captures import Capture
from meerkat.common import CommonException


class TaskExistsError(CommonException): pass


@dataclass
class Config:
    target_url: str
    timeout: float=None


async def streaming(capture: Capture,
                    config: Config,
                    encode: Callable[[np.ndarray], Any]=None):
    try:
        async with websockets.connect(config.target_url) as ws:
            try:
                while True:
                    data = capture.read(config.timeout, encode)
                    await ws.send(data)
                    await asyncio.sleep(0)
            except asyncio.CancelledError:
                pass
            except:
                logger.exception('An exception has occurred within '
                                 'streaming ...')
            finally:
                capture.stop()
                capture.join()
    except:
        logger.exception('An exception has occurred within connecting '
                         'to websocket server ...')


class Streamer(ABC):
    def __init__(self):
        self._task = None
        self._lock = threading.Lock()

    @abstractmethod
    async def start(self, capture: Capture, config: Config):
        pass

    @abstractmethod
    async def stop(self):
        pass


class FrameStreamer(Streamer):
    def __init__(self):
        super().__init__()

    async def start(self, capture: Capture, config: Config):
        with self._lock:
            if self._task is not None:
                raise TaskExistsError(
                    'A streaming task already exists.')
            self._task = asyncio.create_task(
                streaming(capture, config))

    async def stop(self):
        with self._lock:
            if self._task is None:
                return
            self._task.cancel()
            await self._task
            self._task = None
