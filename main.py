import aiohttp

from api.bot.bot_register import bot
from api.ContentTypes import manga, photo, video, all_types, create_union
from api.save_control import SaveContentControl
from api.utils import megabytes_to_bytes

save_path = './data/'


async def main():
    save_content = create_union(manga, photo, video)
    c = SaveContentControl(save_content,
                           save_path=save_path,
                           delete_messages=True,
                           cutoff=megabytes_to_bytes(200))
    async with aiohttp.ClientSession(loop=bot.loop) as session:
        await c.create_download_loop(session, limit=None)

bot.loop.run_until_complete(main())
