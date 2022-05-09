

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup

from src.utilities import Log
logger = Log.getLogger()


def setup(bot):
    bot.add_cog(GeneralCmd(bot))
    logger.debug("Registering GeneralCmd successful")


class GeneralCmd(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(name="invite")
    async def cmd_invite(self, ctx):
        view = discord.ui.View(discord.ui.Button(label="Invite", style=discord.ButtonStyle.primary,
                                                 url="https://discord.com/api/oauth2/authorize?client_id=972317660966694952&permissions=8&scope=bot%20applications.commands"))
        await ctx.respond(view=view)
