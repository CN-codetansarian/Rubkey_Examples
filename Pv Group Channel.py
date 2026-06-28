from rubkey import Rubkey

TOKEN = ""
bot = Rubkey(token=TOKEN)


@bot.command("start")
def start(msg):
    if msg.chat_id.startswith("b"):
        msg.reply("سلام")
    elif msg.chat_id.startswith("c"):
        msg.reply("کانال")


@bot.on_message()
def handle(msg):
    if not msg.text:
        return
    
    if hasattr(msg, 'button_id') and msg.button_id:
        return
    
    if msg.chat_id.startswith("g") and msg.text.strip() == "س":
        msg.reply("گروه")


bot.run()