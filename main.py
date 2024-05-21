import asyncio
import traceback

from meerkat.readers import FrameReader
from meerkat.buffers import FrameBuffer
from meerkat.captures import FrameCapture
from meerkat.streamers import streaming, Config
from config import settings


async def main():
    model = settings.MODEL()
    capture = FrameCapture(FrameReader(settings.VIDEO_SOURCE),
                           FrameBuffer(settings.BUFFER_SIZE))
    capture.start()

    websocket_uri = settings.WEBSOCKET_URI
    timeout_sec = settings.TIMEOUT_SEC
    config = Config(websocket_uri, timeout_sec)

    try:
        await streaming(capture, config, model.encode)
    except:
        traceback.print_exc()
    finally:
        model.release()
        capture.stop(is_released=True)
        capture.join()


if __name__ == '__main__':
    asyncio.run(main())