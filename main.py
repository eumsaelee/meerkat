import asyncio
import traceback

from meerkat.video.readers import FrameReader
from meerkat.video.buffers import FrameBuffer
from meerkat.video.updaters import FrameUpdater
from meerkat.video.streamers import streaming, StreamingConfig
from config import settings


async def main():
    model = settings.MODEL()
    updater = FrameUpdater(FrameReader(settings.VIDEO_SOURCE),
                           FrameBuffer(settings.BUFFER_SIZE),
                           model.encode)
    updater.start()

    websocket_uri = settings.WEBSOCKET_URI
    timeout_sec = settings.TIMEOUT_SEC
    config = StreamingConfig(websocket_uri, timeout_sec)

    try:
        await streaming(updater, config)
    except:
        traceback.print_exc()
    finally:
        model.release()
        updater.stop(is_released=True)
        updater.join()


if __name__ == '__main__':
    asyncio.run(main())