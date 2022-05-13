import sys

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
                                                 url=f"https://discord.com/api/oauth2/authorize?client_id={config['BOT']['client_id']}&permissions=8&scope=bot%20applications.commands"))
        await ctx.respond(view=view)


class TestCmd(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @staticmethod
    def is_bot_dev(ctx):
        role_id = config['BOT']['role_ids']
        for i in role_id:
            role = discord.utils.get(ctx.author.roles, id=int(i))
            if role is None:
                raise commands.MissingRole(role_id)
        return True

    @commands.slash_command(name="ping")
    async def cmd_ping(self, ctx):
        await ctx.respond(f"Pong!\n{round(self.bot.latency, 2)}ms")

    @commands.slash_command(name="breakpoint")
    async def _breakpoint(self, ctx):
        228922 / 0 * (114514 + 1919810)

    admin = SlashCommandGroup("admin", "測試用", checks=[is_bot_dev])

    @admin.command(name="quit")
    async def cmd_quit(self, ctx):
        await ctx.respond('cya~', ephemeral=True)
        sys.exit(0)

    @admin.command(name="echo")
    async def test_echo(self, ctx, msg):
        await ctx.respond(msg)

    error = admin.create_subgroup("error", "for Debug")

    @error.command(name="cmd")
    async def error_cmd(self, _):
        raise commands.CommandError("Test Error")

    @error.command(name="role")
    @commands.has_role(972430880943529986)
    async def error_role(self, ctx):
        await ctx.respond(":interrobang: **I have two???**")
