from api.bot.bot_register import bot


class MessageDeleter:
    async def delete_messages(self, messages):
        async with bot:
            while messages:
                msg = messages.pop()
                if not isinstance(msg, tuple):
                    await msg.delete()
                else:
                    print("Cant delete message: ", msg[0])
        print(f"All downloaded messages were deleted!")
