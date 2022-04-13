
from .command import *
from .event import *



from disnake.ext import commands




class BOT():

    def __init__(self,token=None):
        self.bot = commands.Bot(command_prefix=">")
        if token is not None:
            self.token=token
        else:
            raise AttributeError("Token must be a string.")

    def setup(self):

        self.bot.add_cog(MusicCmd(self.bot))
        self.bot.add_cog(BotEvent(self.bot))

    def run(self):
        self.bot.run(self.token)

    def stop(self):
        pass

    def teardown(self):
        pass

