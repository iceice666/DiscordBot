from .command import *
from .event import *
from . import config


from disnake.ext import commands





class BOT():
    def __init__(self):
        self.bot = commands.Bot(command_prefix=">")

    def setup(self):

        self.bot.add_cog(MusicCmd(self.bot))
        self.bot.add_cog(BotEvent(self.bot))

    def run(self):
        self.bot.run(config.TOKEN)

    def stop(self):
        pass

    def teardown(self):
        pass

