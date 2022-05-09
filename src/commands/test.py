
import sys
from os.path import abspath, join, dirname


import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup

from src.utilities import Log
from src import config

logger = Log.getLogger()


def setup(bot):
    bot.add_cog(TestCmd(bot))
    logger.debug("Registering TestCmd successful")


class TestCmd(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @staticmethod
    def is_botDev(ctx):
        role_id = config.role_botDev
        role = discord.utils.get(
            ctx.author.roles, id=role_id)
        if role is None:
            raise commands.MissingRole(role_id)
        return

    @commands.slash_command(name="breakpoint")
    async def _breakpoint(self,ctx):
        pass

    test = SlashCommandGroup("test", "測試用", checks=[is_botDev])

    @test.command(name="echo")
    async def test_echo(self, ctx, msg):
        await ctx.respond(msg)

    error = test.create_subgroup("error", "for Debug")

    @error.command(name="cmd")
    async def error_cmd(self, _):
        raise commands.CommandError("Test Error")

    @error.command(name="role")
    @commands.has_role(972430880943529986)
    async def error_role(self, ctx):
        ctx.respond(":interrobang: **I have two???**")

    @error.command(name="divide0")
    async def error_div0(self, _):
        114514/0
