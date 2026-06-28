import asyncio
from rubkey import AsyncBot
from rubkey.metadata import Metadata, MetadataPart

TOKEN = ""
bot = AsyncBot(token=TOKEN)


@bot.command("start")
async def start(msg):
    text = "Bold\nلینک\nSpoiler\nنقل قول\nزیر خط خورده"
    
    meta = Metadata()
    meta.add_part(MetadataPart("Bold", 0, 4))
    meta.add_part(MetadataPart("Link", 5, 4, link_url="https://rubika.ir"))
    meta.add_part(MetadataPart("Spoiler", 10, 7))
    meta.add_part(MetadataPart("Quote", 18, 7))
    meta.add_part(MetadataPart("Underline", 26, 11))
    
    await msg.reply(text, metadata=meta)


async def main():
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())