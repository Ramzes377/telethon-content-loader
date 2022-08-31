import os
import aiofiles
from tqdm.asyncio import tqdm

from api.bot.bot_register import bot
from api.downloaders.basedownloader import BaseDownloader
from api.downloaders.manga_downloader import MangaDownloader
from api.utils import megabytes_to_bytes, bytes_to_megabytes


class MediaDownloader(BaseDownloader):
    request_size = megabytes_to_bytes(15)

    def __init__(self, content_types, base_path, relative_path='media', **kw):
        super(MediaDownloader, self).__init__(base_path=base_path, relative_path=relative_path, **kw)
        self._requested_content = content_types

    async def download(self, session, msg):
        if msg.media is None:
            return
        try:
            filename = msg.document.attributes[0].__dict__['file_name']
        except (AttributeError, KeyError):
            filename = f'{msg.id}{msg.grouped_id if msg.grouped_id else ""}{msg.file.ext}'
        file_path = os.path.join(self._path, filename)

        size = msg.file.size
        if os.path.exists(file_path) and os.path.getsize(file_path) == size:                                                    # file already downloaded
            return msg

        is_message_manga = await MangaDownloader.is_message_contains_manga(session, msg)
        if is_message_manga:                                                                                                    # do nothing if message is manga, otherwise it download cover and delete this message
            return

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
                                            desc=filename, unit='B', unit_scale=True,
                                            total=int(size/MediaDownloader.request_size),
                                            position=self.files[filename], mininterval=5, leave=True):
                        await file.write(chunk)
                return msg
            else:
                print('TYPE', type(msg.media))
        except Exception as e:
            print("Error with download: ", e)
