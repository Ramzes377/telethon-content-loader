import os
from api.utils import megabytes_to_bytes, create_path


class BaseDownloader(object):
    VERY_LARGE_FILE_SIZE_BYTES = megabytes_to_bytes(150)  # default is larger than 50MB
    files = {}  # contains positions of file in callback queue
    base_path = './'
    relative_path = '/'

    def __init__(self, *_, **kwargs):
        base_path = kwargs.get('base_path') or BaseDownloader.base_path
        relative_path = kwargs.get('relative_path') or BaseDownloader.relative_path
        self._path = os.path.join(base_path, relative_path)
        create_path(self._path)
        BaseDownloader.VERY_LARGE_FILE_SIZE_BYTES = kwargs.get('cutoff') if kwargs.get('cutoff') is not None \
            else BaseDownloader.VERY_LARGE_FILE_SIZE_BYTES

    async def download(self, *args, **kwargs):
        return
