


from disnake.ext import commands

class BotEvent(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self,ctx,exc):

        msg=[
        "**:middle_finger: U Idiot!**",
        f":x: **{exc}**  :face_with_symbols_over_mouth:"
        ]
        await ctx.send("\n".join(msg))

