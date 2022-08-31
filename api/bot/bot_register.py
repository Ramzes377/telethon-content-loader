from telethon.sync import TelegramClient
import os

with open(os.path.abspath('./api/bot/config.ini')) as file:
	api_id = int(next(file))
	api_hash = next(file).strip()
	username = next(file).strip()

bot = TelegramClient(username, api_id, api_hash)
bot.start()
