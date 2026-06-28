import asyncio
from rubkey import AsyncBot

TOKEN = ""
bot = AsyncBot(token=TOKEN)


@bot.command("start")
async def start(msg):
    await msg.reply(
        f"سندر ایدی: {msg.sender_id}"
        f"\nچت ایدیت: {msg.chat_id}"
    )


async def main():
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())