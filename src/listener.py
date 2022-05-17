import logging

import discord
from discord.ext import commands


def setup(bot):
    bot.add_cog(Listener(bot))


class Listener(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.getLogger('DiscordBot').info("READY!")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, exc):

        err: any
        error_msg: any

        if isinstance(exc, discord.errors.ApplicationCommandInvokeError):
            err = exc.original
        elif isinstance(exc, commands.CheckFailure):
            err = exc
        else:
            err = exc

        match err.__class__:
            case commands.CommandError:
                await ctx.respond(err.args[0], ephemeral=True)

            case commands.MissingRole:
                role = (await commands.RoleConverter().convert(ctx, str(err.missing_role)))
                logging.getLogger(f'DiscordBot.Guild.{ctx.guild}').warning(
                    f"\n {ctx.author.nick}[{ctx.author.name}#{ctx.author.discriminator}]{ctx.author.mention} \
                    @ Guild {ctx.guild.name}<{ctx.guild.id}> :\n   Missing role {role.name}{role.mention}", extra={'classname': __name__})
                await ctx.respond(f":no_entry_sign: 你沒有 {role.mention} 身分組！")

            case _ as e if e is not SystemExit:
                logging.getLogger(f'DiscordBot.Guild.{ctx.guild}').error(
                    f"\n{exc}\n", exc_info=1)
