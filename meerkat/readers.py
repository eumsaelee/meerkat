"""
    Exceptions:
        - FailedOpenError
        - FailedReadError

    Interfaces:
        - Reader

    Classes:
        - FrameReader(Reader)
"""

import threading
from typing import Union
from abc import ABC, abstractmethod

import cv2
import numpy as np

from meerkat.common import CommonException


class FailedOpenError(CommonException): pass
class FailedReadError(CommonException): pass


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
            self._cap.release()
            self._cap.open(value)
            if not self._cap.isOpened():
                raise FailedOpenError(
                    f'Failed to open {self._video_source!r}.')
            else:
                self._video_source = value

    def read(self) -> np.ndarray:
        with self._lock:
            ret, frame = self._cap.read()
            if not ret:
                raise FailedReadError(
                    f'Failed to read frame from {self._video_source!r}')
        return frame

    def release(self):
        with self._lock:
            self._cap.release()

    def __repr__(self) -> str:
        return f'FrameReader(video_source={self._video_source!r})'
