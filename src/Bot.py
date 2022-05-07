
import config


import discord


bot = discord.Bot(owner_id='702352975879864416')




@bot.event
async def on_ready():
    print("ready!")


bot.load_extension('command')
bot.run(config.bot_token)

