
from calendar import c
import time
import re

from bs4 import BeautifulSoup
import urllib3

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.utils import escape_markdown
import wavelink

from .player import PLAYER
from .... import config


class MusicCmd(commands.Cog):

    def __init__(self, bot):

        self._menu = None
        self.bot = bot
        self.players: dict[int, PLAYER] = {}
        self._player = None

        self._http = urllib3.poolmanager.PoolManager()

        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        # noinspection SpellCheckingInspection
        await wavelink.NodePool.create_node(bot=self.bot,
                                            host=config['Lavalink']['Host'],
                                            port=config['Lavalink']['Port'],
                                            password=config['Lavalink']['Password'],
                                            https=config['Lavalink']['Secure'])

    async def cog_before_invoke(self, ctx):
        self._player = self.players[ctx.guild_id]

    def get_player(self, guild: discord.Guild = None):

        if self._player is None:
            return
        elif guild is None:
            return self._player.get_player()
        else:
            return self.players[guild.id]

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.players[guild.id] = PLAYER(guild)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.application_id and after.channel is None:
            player = self.get_player()
            if player is None:
                return
            await player.disconnect()

    @staticmethod
    def _is_author_in_vc():
        def predicate(ctx):
            if ctx.author.voice is None:
                raise commands.CommandError("??????????????????????????????")
            return True
        return commands.check(predicate)

    @staticmethod
    def _is_bot_joined():
        def predicate(ctx):
            if ctx.guild.voice_client is None:
                raise commands.CommandError("?????????????????????????????????")
            return True
        return commands.check(predicate)

    music = SlashCommandGroup("music", "?????????")

    # & join
    @music.command(name="join", description='???bot??????????????????')
    @_is_author_in_vc()
    async def music_join(self, ctx):

        await self._player.join(ctx)
        await ctx.respond(":two_hearts: ?????????~ :cupid:")

    # & leave
    @music.command(name="leave", description='???bot????????????')
    @_is_author_in_vc()
    async def music_leave(self, ctx):

        if self.get_player() is None:
            await ctx.respond(":question:???:exclamation:")
            return
        await self._player.leave()
        await ctx.respond(":broken_heart: Ok bye... :broken_heart:")

    # & pause
    @music.command(name="pause", description='??????')
    @_is_author_in_vc()
    async def music_pause(self, ctx):

        await self._player.pause()
        await ctx.respond("paused")

    # & resume
    @music.command(name="resume", description='????????????')
    @_is_author_in_vc()
    async def music_resume(self, ctx):
        await self._player.resume()
        await ctx.respond("Unpaused")

    # & nowplaying
    @music.command(name="nowplaying", description='????????????')
    async def music_nowplaying(self, ctx):
        player = self.get_player()

        await ctx.respond(
            '\n'.join([
                f':sleeping: ?????????...' if player is None or player.source is None
                else ':musical_note: ????????????:\n**{}**\n{} / {}'.format(
                    escape_markdown(player.source.title),
                    time.strftime("%H:%M:%S", time.gmtime(player.position)),
                    time.strftime("%H:%M:%S", time.gmtime(
                        player.source.duration))
                )
            ])
        )

    # & queue
    @music.command(name="queue", description='??????')
    @_is_bot_joined()
    async def music_queue(self, ctx):
        player = self.get_player()

        number_map = {"1": ":one:", "2": ":two:", "3": ":three:", "4": ":four:",
                      "5": ":five:", "6": ":six:", "7": ":seven:", "8": ":eight:", "9": ":nine:", "0": ":zero:"}

        i: int = 0
        index = str
        respond_str = []

        if player is not None or player.source is not None:
            if player.is_playing():
                respond_str.append(":musical_note: ????????????:")
                respond_str.append(
                    f"**{escape_markdown(player.source.title)}**")
                respond_str.append(f"By: __{player.source.author}__")
            else:
                respond_str.append(":sleeping: ?????????...")
        else:
            respond_str.append(":sleeping: ?????????...")

        respond_str.append(':notes: ??????:')

        for song in player.queue:
            i = i + 1
            if len(player.queue) > 9:
                if 10 <= i <= 99:
                    index = str(i)
                elif 1 <= i <= 9:
                    index = "0" + str(i)
            else:
                index = str(i)

            respond_str.append(
                f'{"".join([number_map[a] for a in list(index)])}  {song.title}')
            respond_str.append(
                f"{'       ' * len(index)}__{song.author}__")
        respond_str.append(f'')
        respond_str.append(
            f':repeat_one: **????????????**  {":white_check_mark: " if self._player.song_repeat else ":x:"}')
        respond_str.append(
            f':repeat: **????????????**  {":white_check_mark: " if self._player.queue_loop else ":x:"}')

        return await ctx.respond('\n'.join(respond_str))

    # & storage
    # TODO: move to quickplay
    @music.command(name="storage", description='??????????????????')
    async def music_playlist_return(self, ctx):
        player = self.get_player()
        return await ctx.respond(';'.join([song.uri for song in player.queue]))

    # & remove
    @music.command(name="remove", description='????????????????????????')
    @_is_author_in_vc()
    async def music_remove(self, ctx, by_index: discord.Option(int) or None = None):
        class _Selection(discord.ui.View):
            def __init__(self, queue):
                super().__init__(timeout=60)
                self.ctx = ctx
                self.add_item(self._Menu(queue))

            async def on_timeout(self) -> None:
                self.ctx.edit(content='???????????????!', view=None)

            class _Menu(discord.ui.Select):
                def __init__(self, queue):
                    super().__init__(placeholder="???queue?????????????????????????????????????????? ")
                    self.queue = queue

                    self.add_option(label="??????", value='cancel')
                    for i, track in enumerate(self.queue):
                        if len(str(escape_markdown(track.title))) > 100:
                            continue
                        self.add_option(label=escape_markdown(
                            track.title), value=i, description=track.author)

                async def callback(self, interaction):
                    if self.values[0] == 'cancel':
                        return await interaction.response.edit_message(content='?????????',
                                                                       view=None)

                    track = self.queue[int(self.values[0])]

                    return await interaction.response.edit_message(content=f'?????? {track.title} ?',
                                                                   view=_Remove(int(self.values[0])))

        class _Remove(discord.ui.View):
            def __init__(self, track_index):
                super().__init__(timeout=10)
                self.add_item(self._Cancel())
                self.add_item(self._Confirm(track_index))

            async def on_timeout(self) -> None:
                await super().on_timeout()

            class _Cancel(discord.ui.Button):
                def __init__(self):
                    super().__init__(label="Cancel",  style=discord.ButtonStyle.primary)

                async def callback(self,  interaction):
                    await interaction.response.edit_message(content='?????????!', view=None)

            class _Confirm(discord.ui.Button):
                def __init__(self, track_index):
                    super().__init__(label="Confirm", style=discord.ButtonStyle.danger)
                    self.track_index = track_index

                async def callback(self,  interaction):
                    player = MusicCmd.get_player()
                    track_title = player.queue._queue[self.track_index].title
                    player.queue._queue.remove(
                        player.queue._queue[self.track_index])
                    await interaction.response.edit_message(content=f'????????? **{track_title}**', view=None)

        player = self.get_player()
        if by_index is not None:
            return await ctx.respond(content=f'?????? {player.queue._queue[by_index].title} ?',
                                     view=_Remove(track_index=by_index-1))
        elif by_index is None:
            return await ctx.respond(view=_Selection(player.queue._queue))

    # & clear
    @music.command(name="clear", description='????????????')
    @_is_author_in_vc()
    async def music_clear(self, ctx):
        await self._player.clear()
        await ctx.respond(content="Cleared!")

    # & stop
    @music.command(name="stop", description='???????????????????????????')
    @_is_author_in_vc()
    async def music_stop(self, ctx):
        await self._player.clear()
        await self._player.skip()
        await ctx.respond("Stop!")

    # & repeat
    @music.command(name="repeat", description='????????????')
    @_is_author_in_vc()
    async def music_repeat(self, ctx, toggle: discord.Option(bool) or None = None):
        await self._player.repeat(toggle)
        return await ctx.respond(
            f':repeat_one: **????????????**  {":white_check_mark: " if self._player.song_repeat else ":x:"}')

    # & loop
    @music.command(name="loop", description='????????????')
    @_is_author_in_vc()
    async def music_loop(self, ctx, toggle: discord.Option(bool) or None = None):
        await self._player.loop(toggle)
        return await ctx.respond(
            f':repeat: **????????????**  {":white_check_mark: " if self._player.queue_loop else ":x:"}')

    # & skip
    @music.command(name="skip", description='??????')
    @_is_author_in_vc()
    @_is_bot_joined()
    async def music_skip(self, ctx):
        await self._player.skip()
        await ctx.respond(":fast_forward: ?????????")

    # & play

    @music.command(name="play", description='?????????')
    @_is_author_in_vc()
    async def searching_args_parse(
            self, ctx,
            searches=None,
            loop: discord.Option(bool) or None = None,
            repeat: discord.Option(bool) or None = None):

        def _build_track_selector(tracks):
            _dicted_tracks = {}
            _view = discord.ui.View()
            _view.on_timeout = lambda: ctx.edit(view=None)

            _menu = discord.ui.Select(placeholder="???????????????????????????????????????")
            _menu.add_option(label="??????", value='cancel')
            for track in tracks:
                if len(escape_markdown(track.title)) > 100:
                    continue
                _menu.add_option(
                    label=escape_markdown(track.title), value=track.identifier, description=track.author)

                _dicted_tracks[track.identifier] = track

                async def callback(interaction):
                    if interaction.data["values"][0] == 'cancel':
                        await interaction.response.edit_message(content='???????????????', view=None)
                        return
                    await self._player.add_track(_dicted_tracks[interaction.data["values"][0]])
                    await interaction.response.edit_message(
                        content=f'?????? **{escape_markdown(track.title)}** ?????????????????????', view=None)

            _menu.callback = callback

            _view.add_item(_menu)

            return _view

        player = self.get_player()

        if searches is None:
            if player is not None and player.is_paused():
                await self.music_resume(ctx)
            return

        if player is None:
            await self._player.join(ctx)

        if loop is not None:
            await self._player.loop(loop)
        if repeat is not None:
            await self._player.repeat(repeat)

        node = self._player.get_node()

        async def _request(search):
            if search == "":
                return

            await ctx.respond(
                f":musical_note: **Searching** :mag_right: {escape_markdown(search)}")

            if re.search(r"(https?:)?\/\/((www\.youtube\.com\/watch\?v=)|(youtu\.be\/))[\w\-]{11}", search):
                searched_track = (await node.get_tracks(
                    cls=wavelink.SearchableTrack,
                    query="ytsearch:{}".format(
                        BeautifulSoup(self._http.request(
                            'GET', search).data, features='html.parser').title.string
                        # search
                    )
                ))[0]
                await self._player.add_track(searched_track)

            else:
                while 1:
                    searched_tracklist = await wavelink.YouTubeTrack.search(search)
                    if len(searched_tracklist) >= 1:
                        break

                await ctx.interaction.edit_original_message(view=_build_track_selector(searched_tracklist))

            msg = f'?????? **{escape_markdown(searched_track.title)}** ?????????????????????'

            await ctx.interaction.edit_original_message(content=msg)

            if not self.get_player().is_playing():
                await self._player.play_track()

        for search in searches.split(";"):
            await _request(search)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        await self._player.playing_finished(player, track, reason)
