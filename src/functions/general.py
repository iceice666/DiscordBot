import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands

from src import config




class GeneralCmd(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(name="invite")
    async def cmd_invite(self, ctx):
        view = discord.ui.View(discord.ui.Button(label="Invite", style=discord.ButtonStyle.primary,
                                                 url=f"https://discord.com/api/oauth2/authorize?client_id={config.bot_client_id}&permissions=8&scope=bot%20applications.commands"))
        await ctx.respond(view=view)


class TestCmd(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @staticmethod
    def is_bot_dev(ctx):
        role_id = config.role_botDev
        role = discord.utils.get(
            ctx.author.roles, id=role_id)
        if role is None:
            raise commands.MissingRole(role_id)
        return

    @commands.slash_command(name="ping")
    async def cmd_ping(self, ctx):
        await ctx.respond(f"Pong!\n{round(self.bot.latency, 2)}ms")

    @commands.slash_command(name="breakpoint")
    async def _breakpoint(self, ctx):
        pass

    test = SlashCommandGroup("test", "測試用", checks=[is_bot_dev])

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
        114514 / 0
