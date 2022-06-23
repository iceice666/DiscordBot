
import wavelink
from discord.utils import escape_markdown
from discord.ext import commands
import discord

import logging



class PLAYER:
    def __init__(self, guild: discord.Guild):
        self.song_repeat = False
        self.queue_loop = False
        self.skip_flag = False

        self.guild: discord.Guild = guild

    def get_node(self):
        return wavelink.NodePool.get_node()

    def get_player(self):
        return wavelink.NodePool.get_node().get_player(self.guild)

    async def play_track(self):
        player = self.get_player()

        np = await player.queue.get_wait()
        logging.getLogger(f"DiscordBot.Guild.{self.guild}").info(
            f"Now playing: '{np}'", extra={'classname': __name__})
        await player.play(np)

    async def add_track(self, track):
        player = self.get_player()
        await player.queue.put_wait(track)

    async def playing_finished(self, player, track, reason):
        logger = logging.getLogger(f'DiscordBot.Guild.{player.guild}')
        logger.info(
            f"Finished playing: {escape_markdown(track.title)} [{reason}]", extra={'classname': __name__})

        match reason:
            case "LOAD_FAILED":
                logger.warning("無法載入歌曲！")
                commands.CommandError("**無法載入歌曲！**\n**請重新加入歌單！**")

            case "STOPPED" if self.skip_flag:
                self.skip_flag = False

            case "STOPPED":
                if self.queue_loop:
                    player.queue.put(track)

            case "FINISHED":
                if self.song_repeat:
                    player.queue.put_at_front(track)
                elif self.queue_loop:
                    player.queue.put(track)

        await self.play_track()

    async def repeat(self, toggle:bool):
        if toggle is not None:
            self.song_repeat = toggle

    async def loop(self, toggle:bool):
        if toggle is not None:
            self.queue_loop = toggle

    async def skip(self):
        player = self.get_player()

        self.skip_flag = True
        await player.stop()

    async def clear(self):
        player = self.get_player()
        if not player.queue.is_empty:
            player.queue.clear()

    async def join(self, ctx=None):
        if ctx is None:
            return

        player = self.get_player()
        if player is None:
            await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            await player.move_to(ctx.author.voice.channel)

    async def leave(self):
        player = self.get_player()
        await player.disconnect()

    async def pause(self):
        player = self.get_player()
        if player.is_playing() and not player.is_paused():
            await player.pause()

    async def resume(self):
        player = self.get_player()
        if player.is_paused():
            player.resume()
