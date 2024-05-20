from . import models


MODEL = models.Yolov8n

VIDEO_SOURCE = 'rtsp://192.168.1.101:12554/profile2/media.smp'

BUFFER_SIZE = 1

WEBSOCKET_URI = 'ws://172.27.1.12:8000/ws/stream/21/'

TIMEOUT_SEC = 30