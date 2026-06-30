import asyncio
from rubkey import AsyncBot, Keypad, KeyButton

TOKEN = ""
bot = AsyncBot(token=TOKEN)

main_keypad = Keypad(resize=True).add_row(
    KeyButton("dokme", "دکمه"),
    KeyButton("n", "بعدی")
)

back_keypad = Keypad(resize=True).add_row(
    KeyButton("h", "برگشت")
)


@bot.command("start")
async def start(msg):
    await msg.reply("سلام", keypad=main_keypad)


@bot.on_button("dokme")
async def dokme(msg):
    await msg.reply("چه خبر")


@bot.on_button("n")
async def n(msg):
    await msg.reply("اینم بعدی", keypad=back_keypad)


@bot.on_button("h")
async def h(msg):
    await msg.reply("خب برگشت خورد", keypad=main_keypad)


async def main():
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())