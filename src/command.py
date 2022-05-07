

import pathlib
from typing import Optional
import wavelink
from pprint import pprint

import discord
from discord.ext import commands


import re


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(MusicCmd(bot))  # add the cog to the bot


class MusicCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.songRepeat = False
        self.queueLoop = False

        self.playlist = []
        self.nowplaying = {}

        self._download_list = []

        bot.loop.create_task(self.connect_nodes())

    @commands.Cog.listener("on_command_error")
    async def command_error(self, ctx, exc):

        msg = [
            "**:middle_finger: U Idiot!**",
            f":x: **{exc}**  :face_with_symbols_over_mouth:"
        ]
        await ctx.respond("\n".join(msg))

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(bot=self.bot,
                                            host="lavalink.oops.wtf",
                                            port=2000,
                                            password="www.freelavalink.ga")

        print("lavalink connected")

    def _in_vc_check(self, ctx):
        if ctx.author.voice is None:
            raise commands.CommandError(
                "U to need join a voice channel first!")

    @discord.slash_command(name="echo")
    async def cmdtest_echo(self, ctx, msg):
        await ctx.respond(msg)

    @discord.slash_command(name="error")
    async def cmdtest_error(self, ctx):
        raise commands.CommandError("U noob")

    @discord.slash_command(name="invite")
    async def cmdtest_invite(self, ctx):
        ctx.send("https://discord.com/api/oauth2/authorize?client_id=972317660966694952&permissions=8&scope=bot%20applications.commands")

    @discord.slash_command(name="join")
    async def cmd_join(self, ctx):
        self._in_vc_check(ctx)

        if ctx.voice_client is None:
            await ctx.respond(":heart: 我要進來嘍~ :heart:")
            await ctx.author.voice.channel.connect()

        elif ctx.voice_client.channel.id == ctx.author.voice.channel.id:
            await ctx.respond(":rage: 你已經有一個了！ :middle_finger:")
            return

        else:
            await ctx.respond(":two_hearts: 我來啦~ :cupid:")
            await ctx.voice_client.move_to(ctx.author.voice.channel)

        return

    @discord.slash_command(name="leave")
    async def cmd_leave(self, ctx):
        self._in_vc_check(ctx)
        if ctx.voice_client is None:
            await ctx.respond(":question:???:exclamation:")
            return
        await ctx.voice_client.disconnect()
        await ctx.respond(":broken_heart: Ok bye... :broken_heart:")

    @discord.slash_command(name="pause")
    async def cmd_pause(self, ctx):
        self._in_vc_check(ctx)
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

    @discord.slash_command(name="volume")
    async def cmd_volume(self, ctx, vol: Optional[discord.Option(int, min_value=0, max_value=100)]=None):
        if vol is None:
            #TODO return wavelink player vol
            pass

        number_map = {"1": ":one:", "2": ":two:", "3": ":three:", "4": ":four:",
                      "5": ":five:", "6": ":six:", "7": ":seven:", "8": ":eight:", "9": ":nine:", "0": ":zero:"}

        if vol == 0:
            vol_str = "000"
        elif vol == 100:
            vol_str = "100"
        else:
            vol_str = "0"+str(vol)
        respond_str = ":speaker:" + \
            " ".join([number_map[a] for a in list(vol_str)])

        await ctx.respond(respond_str)

        #TODO set player volume


    @discord.slash_command(name="play")
    async def cmd_play(self, ctx, *, url: discord.Option(str) or None = None):
        self._in_vc_check(ctx)
        if ctx.voice_client is None:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

        elif url is None:
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
                return
            else:
                raise commands.BadArgument(
                    "Is ur URL link has been eaten by Paimon?")

        ytUrl = re.match(
            "http[s]?:\/\/(www.youtube.com\/watch\?v=|youtu.be\/)[-_\d\w]{11}", url).group()

        ytCode = ytUrl.replace("?", "/").split("/")[-1]

        matched_files = list(pathlib.Path("./audioCache").glob(f"{ytCode}.*"))

        if not matched_files:
            await self._ytdl(ytCode)
        else:
            if ctx.voice_client.is_connected() and not (ctx.is_playing() and ctx.is_paused()):

                # TODO play music
                pass

            else:
                self.playlist.append({ytCode: matched_files[0]})

    def _playing_end(self, error=None):
        if self.songRepeat:
            self.playlist.insert(0, self.nowplaying)
        elif self.queueLoop:
            self.playlist.append(self.nowplaying)
