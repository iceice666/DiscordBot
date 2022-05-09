
import discord
from discord.ext import commands

from src.utilities import Log,log_and_respond
from src import i18n
from src.i18n import CONSOLE,TRANSLATION

def setup(bot):
    bot.add_cog(listener(bot))


class listener(commands.Cog):

    logger = Log.getLogger()

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("READY!")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, exc):

        global err, error_msg

        if isinstance(exc, discord.errors.ApplicationCommandInvokeError):
            err = exc.original
        elif isinstance(exc, commands.CheckFailure):
            err = exc

        match err.__class__:
            case commands.CommandError:

                await log_and_respond(ctx, self.logger,"debug", i18n,err.args[0])
                return

            case commands.MissingRole:
                role = (await commands.RoleConverter().convert(ctx, str(err.missing_role)))
                self.logger.warning(
                    f"\n {ctx.author.nick}[{ctx.author.name}#{ctx.author.discriminator}]{ctx.author.mention} @ Guild {ctx.guild.name}<{ctx.guild.id}> :\n   Missing role {role.name}{role.mention}")
                await ctx.respond(f":no_entry_sign: 你沒有 {role.mention} 身分組！")
                return

        self.logger.error(f"\n{exc}\n", exc_info=1)
        await ctx.respond(f":x: **{exc}**")
