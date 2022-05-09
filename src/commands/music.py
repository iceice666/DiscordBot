

import pathlib
import wavelink
import re

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option

from src.utilities import Log
from src.i18n import CONSOLE

logger = Log.getLogger()


def setup(bot):
    bot.add_cog(MusicCmd(bot))
    logger.debug("Registering MusicCmd successful")


class MusicCmd(commands.Cog):

    logger = Log.getLogger()

    def __init__(self, bot):

        self.bot = bot

        self.songRepeat = False
        self.queueLoop = False

        self.playlist = []
        self.nowplaying = {}

        self._download_list = []

        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(bot=self.bot,
                                            host="lavalink.oops.wtf",
                                            port=2000,
                                            password="www.freelavalink.ga")

        self.logger.info("Lavalink server connected")

    def _is_author_in_vc(self, ctx):
        if ctx.author.voice is None:
            raise commands.CommandError("author_not_in_vc")
        return True

    def _is_bot_joined(self, ctx):
        if ctx.guild.voice_client is None:
            raise commands.CommandError("bot_not_joined")
        return True

    def getPlayer(self, ctx):

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)
        return player

    music = SlashCommandGroup("music", "音樂用")

    @music.command(name="join")
    async def music_join(self, ctx):
        self._is_author_in_vc(ctx)
        player = self.getPlayer(ctx)

        if player is None:
            await ctx.respond(":heart: 我要進來嘍~ :heart:")
            await ctx.author.voice.channel.connect(cls=wavelink.Player)

        elif player.channel.id == ctx.author.voice.channel.id:
            await ctx.respond(":rage: 你已經有一個了！ :middle_finger:")
            return

        else:
            await ctx.respond(":two_hearts: 我來啦~ :cupid:")
            await player.move_to(ctx.author.voice.channel)

        return

    @music.command(name="leave")
    async def music_leave(self, ctx):
        self._is_author_in_vc(ctx)
        player = self.getPlayer(ctx)
        if player is None:
            await ctx.respond(":question:???:exclamation:")
            return
        await player.disconnect()
        await ctx.respond(":broken_heart: Ok bye... :broken_heart:")

    @music.command(name="pause")
    async def music_pause(self, ctx):
        self._is_author_in_vc(ctx)
        player = self.getPlayer(ctx)
        if player.is_playing():
            await player.pause()

    @music.command(name="volume")
    async def music_volume(self, ctx, vol: Option(int, min_value=0, max_value=100) or None = None):
        self._is_bot_joined(ctx)

        player = self.getPlayer(ctx)
        if vol is None:
            vol = player.volume

        number_map = {"1": ":one:", "2": ":two:", "3": ":three:", "4": ":four:",
                      "5": ":five:", "6": ":six:", "7": ":seven:", "8": ":eight:", "9": ":nine:", "0": ":zero:"}

        if vol == 0:
            vol_str = "000"
        elif vol == 100:
            vol_str = "100"
        elif vol >= 1 and vol <= 9:
            vol_str = "00"+str(vol)
        elif vol >= 10 and vol <= 99:
            vol_str = "0"+str(vol)

        respond_str = ":speaker:" + \
            " ".join([number_map[a] for a in list(vol_str)])

        if vol > player.volume:
            respond_str += " :arrow_up_small:"
        elif vol < player.volume:
            respond_str += " :arrow_down_small:"

        await player.set_volume(vol)

        return await ctx.respond(respond_str)

    @music.command(name="play")
    async def music_play(self, ctx, *, url: discord.Option(str) or None = None):
        self._is_author_in_vc(ctx)
        player = self.getPlayer(ctx)
        if player is None:
            await player.move_to(ctx.author.voice.channel)

        elif url is None:
            if player.is_paused():
                await player.resume()
                return
            else:
                raise commands.BadArgument(
                    "Is ur URL link has been eaten by Paimon?")

        ytUrl = re.match(
            "http[s]?:\/\/(www.youtube.com\/watch\?v=|youtu.be\/)[-_\d\w]{11}", url).group()

        ytCode = ytUrl.replace("?", "/").split("/")[-1]

        matched_files = list(pathlib.Path("./audioCache").glob(f"{ytCode}.*"))

        if player.is_connected() and not (ctx.is_playing() and ctx.is_paused()):

            # TODO play music
            pass

        else:
            self.playlist.append({ytCode: matched_files[0]})

    def _playing_end(self, error=None):
        if self.songRepeat:
            self.playlist.insert(0, self.nowplaying)
        elif self.queueLoop:
            self.playlist.append(self.nowplaying)
