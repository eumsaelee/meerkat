import threading
from typing import Union, Any
from abc import ABC, abstractmethod

import cv2
import numpy as np


# --- Exception ---


class FailedOpenError(Exception):
    def __init__(self, video_source: Any):
        message = f'Failed to open {video_source!r}.'
        super().__init__(message)


class FailedReadError(Exception):
    def __init__(self, video_source: Any):
        message = f'Failed to read frame from {video_source!r}'
        super().__init__(message)


# --- Interface ---


class Reader(ABC):
    def __init__(self, video_source: Union[int, str]=None):
        self._video_source = video_source

    @property
    @abstractmethod
    def video_source(self) -> Union[int, str]:
        pass

    @video_source.setter
    @abstractmethod
    def video_source(self, value: Union[int, str]):
        pass

    @abstractmethod
    def read(self) -> np.ndarray:
        pass

    @abstractmethod
    def release(self):
        pass


# --- Class ---


class FrameReader(Reader):
    def __init__(self, video_source: Union[int, str]=None):
        super().__init__(video_source)
        self._cap = cv2.VideoCapture()
        self._lock = threading.Lock()
        if video_source is not None:
            self.video_source = video_source

    @property
    def video_source(self) -> Union[int, str]:
        return self._video_source

    @video_source.setter
    def video_source(self, value: Union[int, str]):
        with self._lock:
            self._cap.open(value)
            if not self._cap.isOpened():
                self._video_source = None
                raise FailedOpenError(value)
            else:
                self._video_source = value

    def read(self) -> np.ndarray:
        with self._lock:
            ret, frame = self._cap.read()
            if not ret:
                raise FailedReadError(self._video_source)
        return frame

    def release(self):
        with self._lock:
            self._cap.release()
            self._video_source = None

    def __repr__(self) -> str:
        return f'FrameReader(video_source={self._video_source!r})'
