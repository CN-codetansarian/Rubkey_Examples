import asyncio
import time
from rubkey.selfbot import SelfBot

bot = SelfBot()


@bot.on_message()
def handle(msg):
    text = msg.text.strip()
    
    if text == "سلام":
        msg.reply("چه خبر")
    
    elif text == "اکانت":
        sent = msg.reply(msg.sender_id)
        if sent:
            time.sleep(5)
            sent.edit("سندر ایدی اکانتت بود")


bot.run()