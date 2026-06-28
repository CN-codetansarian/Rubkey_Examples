import asyncio
from rubkey import AsyncBot, Keypad, KeyButton

TOKEN = ""
bot = AsyncBot(token=TOKEN)

phone_keypad = Keypad(resize=True, one_time=True).add_row(
    KeyButton("po", "اشتراک گذاری شماره", button_type="AskMyPhoneNumber")
)


@bot.command("start")
async def start(msg):
    await msg.reply("سلام خوش اومدی...", keypad=phone_keypad)


@bot.on_button("po")
async def po(msg):
    if msg.text:
        await msg.reply(msg.text)


async def main():
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())