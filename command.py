from rubkey import Rubkey

TOKEN = ""
bot = Rubkey(token=TOKEN)

bot.set_commands([
    {"command": "start", "description": "شروع"}
])

bot.run()
