import asyncio
import threading
import websockets
from dataclasses import dataclass
from abc import ABC, abstractmethod

from loguru import logger

from meerkat.updaters import Updater


# --- Dataclass ---


@dataclass
class StreamingConfig:
    uri: str
    timeout: float=None


# --- Exception ---


class TaskAlreadyExistsError(Exception):
    def __init__(self):
        message = 'A streaming task already exists.'
        super().__init__(message)


# ---Function ---


async def streaming(updater: Updater, config: StreamingConfig):
    try:
        async with websockets.connect(config.uri) as ws:
            try:
                while True:
                    data = updater.read(config.timeout)
                    await ws.send(data)
                    await asyncio.sleep(0)
            except asyncio.CancelledError:
                pass
            except:
                logger.exception('An exception has occurred within '
                                 'streaming ...')
            finally:
                updater.stop()
                updater.join()
    except:
        logger.exception('An exception has occurred within connecting '
                         'to websocket server ...')


# --- Interface ---


class Streamer(ABC):
    def __init__(self):
        self._task = None
        self._lock = threading.Lock()

    @abstractmethod
    async def start(self, updater: Updater, config: StreamingConfig):
        pass

    @abstractmethod
    async def stop(self):
        pass


# --- Class ---


class FrameStreamer(Streamer):
    def __init__(self):
        super().__init__()

    async def start(self, updater: Updater, config: StreamingConfig):
        with self._lock:
            if self._task is not None:
                raise TaskAlreadyExistsError()
            self._task = asyncio.create_task(
                streaming(updater, config))

    async def stop(self):
        with self._lock:
            if self._task is None:
                return
            self._task.cancel()
            await self._task
            self._task = None
