from rubkey import Rubkey

TOKEN = ""
bot = Rubkey(token=TOKEN)


@bot.command("start")
def start(msg):
    msg.reply("سلام")


bot.run()
