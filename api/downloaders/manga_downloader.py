import os
import re
import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm

from api.utils import create_path
from api.downloaders.basedownloader import BaseDownloader


async def download_page(session, to_path, page_num, url):
    try:
        img_format = url.split('.')[-1]
        page_path = os.path.join(to_path, f'{page_num}.{img_format}')
        async with session.get(f'https://telegra.ph/{url}') as resp:
            f = await resp.content.read()
            if not (os.path.exists(page_path) and len(f) == os.path.getsize(page_path)):                                        # if page is not already downloaded
                async with aiofiles.open(page_path, 'wb') as file:
                    await file.write(f)
    except Exception as e:
        print('Error with download page: ', url)


async def is_request_correct(session, msg):
    reference_msg = True if msg.message and re.match('https://telegra.ph/[\w|-]+', msg.message) else False
    try:
        reference_media = True if \
            msg.media.__dict__.get('webpage') and re.match('https://telegra.ph/[\w|-]+',
                                                           msg.media.__dict__['webpage'].url) \
            else False
    except AttributeError:
        return False

    if not (reference_msg or reference_media) or not msg.message:
        return False

    try:
        async with session.get(msg.message) as response:
            r = await response.text()
    except aiohttp.client_exceptions.InvalidURL:
        try:
            async with session.get(msg.media.__dict__['webpage'].url) as response:
                r = await response.text()
        except Exception as e:
            print('Raised exception: ', e)
            return False

    if response.status != 200:
        return False
    return r


def is_supposedly_downloaded(path, img_count):
    num_files = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])
    return num_files == img_count


class MangaDownloader(BaseDownloader):

    def __init__(self, base_path, relative_path='manga'):
        super(MangaDownloader, self).__init__(base_path=base_path, relative_path=relative_path)

    @classmethod
    async def is_message_contains_manga(cls, session, msg):
        return await is_request_correct(session, msg)

    async def download(self, session, msg):
        r = await MangaDownloader.is_message_contains_manga(session, msg)
        if not r:
            return
        soup = BeautifulSoup(r, 'html.parser')
        img_urls = [img_src['src'] for img_src in soup.findAll('img')]
        manga_name = soup.find('header').find('h1').contents[0]
        manga_path = os.path.join(self._path, manga_name)
        create_path(manga_path)
        page_count = len(img_urls)
        BaseDownloader.files[manga_name] = len(self.files)
        async for page_num, url in tqdm(iterable=enumerate(img_urls, start=1),
                                        position=BaseDownloader.files[manga_name],
                                        desc=manga_name, unit='page', unit_scale=True, total=page_count,
                                        leave=True,  mininterval=3,
                                        bar_format='[ {desc:} ] {rate_fmt} [{bar:30}] {percentage:3.0f}%'):
            await download_page(session, manga_path, page_num, url)
        return msg
