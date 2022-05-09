


from src.utilities import Log
from src import config

import discord
from discord.ext import commands


class BOT:

    logger = Log().getLogger()

    bot = discord.Bot(owner_ids=config.owner_ids)



    bot.load_extension('src.commands.music')
    bot.load_extension('src.commands.test')
    bot.load_extension('src.commands.general')
    bot.load_extension('src.listener')

    def run(self):
        self.bot.run(config.bot_token)
