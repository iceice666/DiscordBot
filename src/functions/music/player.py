from os import stat
import wavelink
from discord.utils import escape_markdown
from discord.ext import commands
import discord

import logging
import yarl


class _PLAYER:

    class _View(discord.ui.View):
        def __init__(self, ctx, tracks):
            super().__init__(timeout=60)
            self.ctx = ctx
            self.add_item(self._Menu(tracks))

        async def on_timeout(self) -> None:
            await _PLAYER._add_track('timeout', self.ctx)

        class _Menu(discord.ui.Select):
            def __init__(self, tracks):
                super().__init__(placeholder="為啥你不要直接輸入網址呢？")
                self.tracks = tracks
                self.add_option(label="取消搜尋", value='cancel')
                for track in self.tracks:
                    if len(escape_markdown(track.title)) > 100:
                        continue
                    self.add_option(
                        label=escape_markdown(track.title), value=track.identifier, description=track.author)

            async def callback(self, interaction):
                if self.values[0] == 'cancel':
                    await _PLAYER._add_track('cancel', interaction)
                for track in self.tracks:
                    if track.identifier == self.values[0]:
                        return await _PLAYER._add_track(track, interaction)

    @classmethod
    async def _play(cls, guild):
        player = wavelink.NodePool.get_node().get_player(guild)
        np = await player.queue.get_wait()
        logging.getLogger(f"DiscordBot.Guild.{player.guild}").info(
            f"Now playing: '{np}'", extra={'classname': __name__})
        await player.play(np)

    @classmethod
    async def _add_track(cls, track, context):
        player = wavelink.NodePool.get_node().get_player(context.guild)

        if isinstance(context, discord.Interaction):

            if track == 'cancel':
                await context.response.edit_message(content='搜尋已取消', view=None)
            else:
                await context.response.edit_message(content=f'已將 **{escape_markdown(track.title)}** 加入播放清單中', view=None)
        elif isinstance(context, discord.commands.context.ApplicationContext):
            if track == 'timeout':
                await context.edit(view=None)
            else:
                await context.respond(content=f'已將 **{escape_markdown(track.title)}** 加入播放清單中')

        if isinstance(track, wavelink.Track):
            await player.queue.put_wait(track)
        if not player.is_playing():
            await cls._play(context.guild)

    @classmethod
    async def _run(cls, ctx, searches):
        node = wavelink.NodePool.get_node()
        player = wavelink.NodePool.get_node().get_player(ctx.guild)

        if searches is None:
            if player is not None:
                if player.is_paused():
                    await player.resume()
                    return await ctx.respond("Unpause!")
                else:
                    raise commands.CommandError("missing song name")

        if player is None:
            await ctx.author.voice.channel.connect(cls=wavelink.Player)

        for search in searches.split(";"):
            if search == "":
                return


            check = yarl.URL(search)
            if check.is_absolute() and str(check.host) == 'www.youtube.com' or str(check.host) == 'yout.be':
                try:
                    searched_tracklist = await node.get_tracks(cls=wavelink.SearchableTrack, query=f"ytsearch:{search}")
                    await cls._add_track(searched_tracklist[0], ctx)
                except IndexError:
                    await ctx.respond(f"I cant find {escape_markdown(search)}! Plz try again!")
            else:
                while 1:
                    searched_tracklist = await wavelink.YouTubeTrack.search(search)
                    if len(searched_tracklist) >= 1:
                        break
                await ctx.respond(f":musical_note: **Searching** :mag_right: {escape_markdown(search)}",view=cls._View(ctx, searched_tracklist))
