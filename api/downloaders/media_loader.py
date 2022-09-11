import os
import aiofiles
from telethon.tl.types import MessageMediaUnsupported
from tqdm.asyncio import tqdm
from time import time

from api.bot.bot_register import bot
from api.downloaders.base_loader import BaseDownloader
from api.downloaders.manga_loader import MangaDownloader
from api.utils import megabytes_to_bytes, bytes_to_megabytes


def pseudo_unique_name_generator():
    while True:
        yield str(time())


name_gen = pseudo_unique_name_generator()


class MediaDownloader(BaseDownloader):
    request_size = megabytes_to_bytes(15)

    def __init__(self, content_types: set, base_path: str, relative_path: str = 'media', **kw):
        super(MediaDownloader, self).__init__(base_path=base_path, relative_path=relative_path, **kw)
        self._requested_content = content_types

    async def download(self, session, msg):
        if msg.media is None:
            return

        is_message_manga = await MangaDownloader.is_message_contains_manga(session, msg)
        if is_message_manga:                                                                                                    # do nothing if message is manga, otherwise it download cover and delete this message
            return

        if isinstance(msg.media, MessageMediaUnsupported):
            await msg.download_media(file=os.path.join(self._path, next(name_gen)))
            return msg

        try:
            filename = msg.document.attributes[0].__dict__['file_name']
        except (AttributeError, KeyError):
            filename = f'{msg.id}{msg.grouped_id if msg.grouped_id else ""}{msg.file.ext}'

        file_path = os.path.join(self._path, filename)
        size = msg.file.size
        if os.path.exists(file_path) and os.path.getsize(file_path) == size:                                                    # file already downloaded
            return msg

        if MediaDownloader.VERY_LARGE_FILE_SIZE_BYTES and size > MediaDownloader.VERY_LARGE_FILE_SIZE_BYTES:                    # cutoff messages with very large files then we just skip it
            print(f'Skipping to download a large file: {filename} with size: {bytes_to_megabytes(size)} MB')
            return
        try:
            if type(msg.media) in self._requested_content:
                BaseDownloader.files[filename] = len(self.files)
                async with aiofiles.open(file_path, 'wb') as file:
                    async for chunk in tqdm(iterable=bot.iter_download(msg.file.media,
                                                                       file_size=size,
                                                                       request_size=MediaDownloader.request_size),
                                            desc=filename, unit='segment', unit_scale=True,
                                            total=int(size/MediaDownloader.request_size),
                                            position=self.files[filename], leave=True,  mininterval=3,
                                            bar_format='[ Media: {desc:} ] {rate_fmt} [{bar:30}] {percentage:3.0f}%'):
                        await file.write(chunk)
                return msg
        except Exception as e:
            print("Error with download: ", e)
