import asyncio
from rubkey import AsyncBot
from rubkey.metadata import Metadata, MetadataPart

TOKEN = ""
bot = AsyncBot(token=TOKEN)


@bot.on_message()
async def handle(msg):
    if not msg.chat_id.startswith("g"):
        return
    
    if not msg.text:
        return
    
    text = msg.text.strip()
    
    if text == "سلام":
        profile_text = "مشاهده نمایه"
        
        meta = Metadata()
        meta.add_part(MetadataPart("MentionText", 0, len(profile_text), mention_text_user_id=msg.sender_id))
        
        await msg.reply(profile_text, metadata=meta)


async def main():
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())