import asyncio

from api.bot.bot_register import bot
from api.utils import create_path, bytes_to_megabytes
from api.ContentTypes import manga
from api.downloaders.basedownloader import BaseDownloader
from api.downloaders.manga_downloader import MangaDownloader
from api.downloaders.media_downloader import MediaDownloader
from api.message_deleter import MessageDeleter


class SaveContentControl:
    save_path = './data'
    items = {}

    def __init__(self, save_content: set, save_path: str = None, delete_messages: bool = False, **kw):
        self._save_content = save_content
        self._save_path = save_path or SaveContentControl.save_path
        self._pages_num = 0

        create_path(self._save_path)

        self._download_manga = manga in save_content
        self._save_content.discard(manga)
        self._download_media = bool(self._save_content)
        self._delete_messages = delete_messages

        self._manga_downloader = MangaDownloader(self._save_path) \
            if self._download_manga else BaseDownloader()
        self._media_downloader = MediaDownloader(save_content, self._save_path, cutoff=kw.get('cutoff')) \
            if self._download_media else BaseDownloader()
        self._message_deleter = MessageDeleter() if self._delete_messages else None
        self.inform_user()

    def inform_user(self):
        """ Inform user about key script parameters """
        download_types = f'User define these items: {self._save_content} as content to download!'
        delete = f'WARNING: User define to DELETE messages after downloading!' if self._delete_messages \
            else f'User define to NOT DELETE messages after downloading!'
        cutoff = f'Cutoff large file size is set to: {bytes_to_megabytes(self._media_downloader.VERY_LARGE_FILE_SIZE_BYTES)} MB'
        download_peak = f'Media download request size is set to: {bytes_to_megabytes(self._media_downloader.request_size)} MB'
        whisper = '\n'.join([download_types, delete, cutoff, download_peak]) + '\nInput something for continue . . .\n'
        input(whisper)

    async def create_download_loop(self, session, limit=None):
        groups = []
        async for msg in bot.iter_messages('me', limit=limit):
            groups.append(self._manga_downloader.download(session, msg))
            groups.append(self._media_downloader.download(session, msg))
        try:
            msgs = [msg for msg in await asyncio.gather(*groups) if msg is not None]
            if self._delete_messages:
                await self._message_deleter.delete_messages(msgs)
        except TypeError:
            pass


