
import time
import wavelink

import urllib3
from urllib3.request import RequestMethods
from urllib3.util import parse_url as urlparse
from bs4 import BeautifulSoup

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.utils import escape_markdown


from .player import PLAYER
from .... import config


class MusicCmd(commands.Cog):

    def __init__(self, bot):

        self._menu = None
        self.bot = bot
        self.players: dict[int, PLAYER] = {}
        self._player = None
        self.http = urllib3.PoolManager()

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

    def get_player(self):
        return self._player.get_player()

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.players[guild.id] = PLAYER(guild)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.application_id and after.channel is None:
            try:
                player = self.get_player()
                if player is None:
                    return
                await player.disconnect()
            except AttributeError:
                pass

    @staticmethod
    def _is_author_in_vc():
        def predicate(ctx):
            if ctx.author.voice is None:
                raise commands.CommandError("請問我是要播給誰聽？")
            return True
        return commands.check(predicate)

    @staticmethod
    def _is_bot_joined():
        def predicate(ctx):
            if ctx.guild.voice_client is None:
                raise commands.CommandError("請問空氣可以播音樂嗎？")
            return True
        return commands.check(predicate)

    music = SlashCommandGroup("music", "音樂用")

    # & join
    @music.command(name="join", description='使bot加入當前頻道')
    @_is_author_in_vc()
    async def music_join(self, ctx):

        await self._player.join(ctx)
        await ctx.respond(":two_hearts: 我來啦~ :cupid:")

    # & leave
    @music.command(name="leave", description='使bot離開頻道')
    @_is_author_in_vc()
    async def music_leave(self, ctx):

        if self.get_player() is None:
            await ctx.respond(":question:???:exclamation:")
            return
        await self._player.leave()
        await ctx.respond(":broken_heart: Ok bye... :broken_heart:")

    # & pause
    @music.command(name="pause", description='暫停')
    @_is_author_in_vc()
    async def music_pause(self, ctx):

        await self._player.pause()
        await ctx.respond("paused")

    # & nowplaying
    @music.command(name="nowplaying", description='現正播放')
    async def music_nowplaying(self, ctx):
        player = self.get_player()

        await ctx.respond(
            '\n'.join([
                f':sleeping: 閒置中...' if player is None or player.source is None
                else ':musical_note: 現正播放:\n**{}**\n{} / {}'.format(
                    escape_markdown(player.source.title),
                    time.strftime("%H:%M:%S", time.gmtime(player.position)),
                    time.strftime("%H:%M:%S", time.gmtime(
                        player.source.duration))
                )
            ])
        )

    # & queue
    @music.command(name="queue", description='歌單')
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
                respond_str.append(":musical_note: 現正播放:")
                respond_str.append(
                    f"**{escape_markdown(player.source.title)}**")
                respond_str.append(f"By: __{player.source.author}__")
            else:
                respond_str.append(":sleeping: 閒置中...")
        else:
            respond_str.append(":sleeping: 閒置中...")

        respond_str.append(':notes: 歌單:')

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
            f':repeat_one: **單曲循環**  {":white_check_mark: " if self._player.song_repeat else ":x:"}')
        respond_str.append(
            f':repeat: **歌單循環**  {":white_check_mark: " if self._player.queue_loop else ":x:"}')

        return await ctx.respond('\n'.join(respond_str))

    # & storage
    # TODO: move to quickplay
    @music.command(name="storage", description='輸出歌單列表')
    async def music_playlist_return(self, ctx):
        player = self.get_player()
        return await ctx.respond(';'.join([song.uri for song in player.queue]))

    # & remove
    @music.command(name="remove", description='從歌單中刪除歌曲')
    @_is_author_in_vc()
    async def music_remove(self, ctx, by_index: discord.Option(int) or None = None):
        class _Selection(discord.ui.View):
            def __init__(self, queue):
                super().__init__(timeout=60)
                self.ctx = ctx
                self.add_item(self._Menu(queue))

            async def on_timeout(self) -> None:
                self.ctx.edit(content='操作已過時!', view=None)

            class _Menu(discord.ui.Select):
                def __init__(self, queue):
                    super().__init__(placeholder="用queue指令查詢位置再直接刪除很難嗎 ")
                    self.queue = queue

                    self.add_option(label="取消", value='cancel')
                    for i, track in enumerate(self.queue):
                        if len(escape_markdown(track.title)) > 100:
                            continue
                        self.add_option(
                            label=escape_markdown(track.title), value=i, description=track.author)

                async def callback(self, interaction):
                    if self.values[0] == 'cancel':
                        return await interaction.response.edit_message(content='已取消',
                                                                       view=None)

                    track = self.queue[int(self.values[0])]

                    return await interaction.response.edit_message(content=f'刪除 {track.title} ?',
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
                    await interaction.response.edit_message(content='已取消!', view=None)

            class _Confirm(discord.ui.Button):
                def __init__(self, track_index):
                    super().__init__(label="Confirm", style=discord.ButtonStyle.danger)
                    self.track_index = track_index

                async def callback(self,  interaction):
                    player = MusicCmd.get_player()
                    track_title = player.queue._queue[self.track_index].title
                    player.queue._queue.remove(
                        player.queue._queue[self.track_index])
                    await interaction.response.edit_message(content=f'已刪除 **{track_title}**', view=None)

        player = self.get_player()
        if by_index is not None:
            return await ctx.respond(content=f'刪除 {player.queue._queue[self.track_index].title} ?',
                                     view=_Remove(track_index=by_index-1))
        elif by_index is None:
            return await ctx.respond(view=_Selection(player.queue._queue))

    # & clear
    @music.command(name="clear", description='清除歌單')
    @_is_author_in_vc()
    async def music_clear(self, ctx):
        await self._player.clear()
        await ctx.respond(content="Cleared!")

    # & repeat
    @music.command(name="repeat", description='單曲循環')
    @_is_author_in_vc()
    async def music_repeat(self, ctx, toggle: discord.Option(bool) or None = None):
        await self._player.repeat(toggle)
        return await ctx.respond(
            f':repeat_one: **單曲循環**  {":white_check_mark: " if self._player.song_repeat else ":x:"}')

    # & loop
    @music.command(name="loop", description='歌單循環')
    @_is_author_in_vc()
    async def music_loop(self, ctx, toggle: discord.Option(bool) or None = None):
        await self._player.loop(toggle)
        return await ctx.respond(
            f':repeat: **歌單循環**  {":white_check_mark: " if self._player.queue_loop else ":x:"}')

    # & skip
    @music.command(name="skip", description='跳過')
    @_is_author_in_vc()
    @_is_bot_joined()
    async def music_skip(self, ctx):
        await self._player.skip()
        await ctx.respond(":fast_forward: 已跳過")



    # & play
    @music.command(name="play", description='放音樂')
    @_is_author_in_vc()
    async def searching_args_parse(
            self, ctx,
            searches=None,
            loop: discord.Option(bool) or None = None,
            repeat: discord.Option(bool) or None = None):

        async def _add_track( track):

            if isinstance(track, wavelink.Track):
                await self._player.add_track(track)
            else:
                return

            self._add_track_msg += f'已將 **{escape_markdown(track.title)}** 加入播放清單中\n'

        async def _selector_callback(interaction):
            if interaction.data["values"] == 'cancel':
                await interaction.delete_original_message()
            await _add_track(self.searched_tracklist[interaction.data["values"][0]])

        def _build_selector(tracks, on_timeout_callback: callable, triggered_callback: callable) -> discord.ui.View:
            _view = discord.ui.View()
            _view.on_timeout = on_timeout_callback

            _menu = discord.ui.Select(placeholder="為啥你不要直接輸入網址呢？")
            _menu.add_option(label="取消搜尋", value='cancel')
            for track in tracks:
                if len(escape_markdown(track.title)) > 100:
                    continue
                _menu.add_option(
                    label=escape_markdown(track.title), value=track.identifier, description=track.author)
            _menu.callback = triggered_callback

            _view.add_item(_menu)

            return _view

        player = self.get_player()

        if searches is None:
            if player is not None and player.is_paused():
                await self._player.resume()
                await ctx.respond("Unpause!")
            return

        if player is None:
            await self._player.join(ctx)
            player = self.get_player()

        if loop is not None:
            await self._player.loop(loop)
        if repeat is not None:
            await self._player.repeat(repeat)

        async def _request(search):
            if search == "":
                return

            node = self._player.get_node()

            check = urlparse(search)
            # url
            if check.host in ['www.youtube.com', 'yout.be']:

                searched_tracklist = await node.get_tracks(
                    cls=wavelink.SearchableTrack,
                    query="ytsearch:{}".format(
                        BeautifulSoup(self.http.request(
                            'GET', search).data, features='html.parser').title.string
                        # search
                    )
                )
                await _add_track(searched_tracklist[0])

            # search
            else:
                c = 0
                while 1:
                    c += 1
                    _searched_tracklist = await wavelink.YouTubeTrack.search(search)
                    if len(_searched_tracklist) >= 1 or c > 5:
                        break
                self.searched_tracklist = {}
                for track in _searched_tracklist:
                    self.searched_tracklist[track.identifier] = track
                await ctx.respond(f":musical_note: **Searching** :mag_right: {escape_markdown(search)}",
                                  view=_build_selector(
                                      self.searched_tracklist.values(), ctx.delete, _selector_callback))

        search_list = searches.split(";")
        self._add_track_msg = ""
        self._add_track_count = 0
        await ctx.respond(f"處理中...{self._add_track_count}/{len(search_list)}\n")

        for search in search_list:
            await _request(search)
            self._add_track_count += 1
            await ctx.interaction.edit_original_message(
                content=f"處理中...{self._add_track_count}/{len(search_list)}\n"+self._add_track_msg, view=None)

            if not self.get_player().is_playing():
                await self._player.play_track()

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        await self._player.playing_finished(player, track, reason)
