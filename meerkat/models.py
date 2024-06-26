import gc
from typing import Any, Dict
from abc import ABC, abstractmethod

import cv2
import torch
import numpy as np

import meerkat.payload as Payload


# --- Exceptions ---


class NotTorchModuleError(Exception):
    def __init__(self, model: Any):
        msg = ("Model must be an instance of torch.nn.Module, "
               f"not {type(model)}.")
        super().__init__(msg)


class EncodeError(Exception):
    def __init__(self):
        msg = "Failed to encode the frame."
        super().__init__(msg)


# --- Interfaces ---


class BaseModel(ABC):
    def __init__(self, model: torch.nn.Module):
        if not isinstance(model, torch.nn.Module):
            raise NotTorchModuleError(model)
        self._model = model

    @abstractmethod
    def predict(self, frame: np.ndarray) -> Dict[str, np.ndarray]:
        pass

    def encode(self, frame: np.ndarray) -> bytes:
        preds = self.predict(frame)
        stream = self._serialize(frame, preds)
        return stream

    def release(self):
        param = next(self._model.parameters())
        if param.device.type == "cuda":
            torch.cuda.empty_cache()
            self._model.cpu()
        del self._model
        gc.collect()

    @staticmethod
    def _serialize(frame: np.ndarray,
                   preds: Dict[str, np.ndarray]) -> bytes:

        def img2bytes():
            ret, img = cv2.imencode(".jpg", frame)
            if not ret:
                raise EncodeError()
            img = img.tobytes()
            payload.frame = img

        def map2bytes():
            for key, value in preds.items():
                payload.preds[key].shape.extend(value.shape)
                payload.preds[key].data.extend(value.flatten())

        payload = Payload.Payload()
        img2bytes()
        map2bytes()
        payload = payload.SerializeToString()
        return payload
