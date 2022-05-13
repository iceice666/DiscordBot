import logging
from tabnanny import check

import discord
import wavelink
import yarl
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.utils import escape_markdown

from src import config


class MusicCmd(commands.Cog):

    def __init__(self, bot):

        self._menu = None
        self.bot = bot

        self.songRepeat: dict[int, bool] = {}
        self.queueLoop: dict[int, bool] = {}

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

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.songRepeat[guild.id] = False
            self.queueLoop[guild.id] = False

    @classmethod
    def get_node(cls):
        node = wavelink.NodePool.get_node()
        return node

    @classmethod
    def get_player(cls, guild):
        node = cls.get_node()
        player: wavelink.Player = node.get_player(guild)
        return player

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
    @music.command(name="join")
    @_is_author_in_vc()
    async def music_join(self, ctx):

        player = self.get_player(ctx.guild)

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

    # & leave
    @music.command(name="leave")
    @_is_author_in_vc()
    async def music_leave(self, ctx):

        player = self.get_player(ctx.guild)
        if player is None:
            await ctx.respond(":question:???:exclamation:")
            return
        await player.disconnect()
        await ctx.respond(":broken_heart: Ok bye... :broken_heart:")

    # & pause
    @music.command(name="pause")
    @_is_author_in_vc()
    async def music_pause(self, ctx):

        player = self.get_player(ctx.guild)
        if player.is_playing():
            await player.pause()
        await ctx.respond("paused")

    # & nowplaying
    # TODO seek the duration
    @music.command(name="nowplaying")
    async def music_nowplaying(self, ctx):
        player = self.get_player(ctx.guild)

        def minute(sec): return f'{int(sec // 60)}:{int(sec % 60)}'

        await ctx.respond(
            '\n'.join([
                f':sleeping: 閒置中...' if player is None or player.source is None
                else f':musical_note: 現正播放:\n**{escape_markdown(player.source.title)}**',
                     f'{minute(player.position)}/{minute(player.source.duration)}'
            ])
        )

    # & queue
    @music.command(name="queue")
    @_is_bot_joined()
    async def music_queue(self, ctx):
        player = self.get_player(ctx.guild)

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
                respond_str.append(f"Youtuber: {player.source.author}")
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
                f"{'       ' * len(index)}Youtuber: {player.source.author}")
        respond_str.append(f'')
        respond_str.append(
            f':repeat_one: **單曲循環**  {":white_check_mark: " if self.songRepeat[ctx.guild.id] else ":x:"}')
        respond_str.append(
            f':repeat: **歌單循環**  {":white_check_mark: " if self.queueLoop[ctx.guild.id] else ":x:"}')

        return await ctx.respond('\n'.join(respond_str))

    # & remove
    # TODO remove song

    # & clear
    @music.command(name="clear")
    @_is_author_in_vc()
    async def music_clear(self, ctx):
        player = self.get_player(ctx.guild)
        if player.queue.is_empty:
            pass
        else:
            player.queue.clear()

    # & repeat
    @music.command(name="repeat")
    @_is_author_in_vc()
    async def music_repeat(self, ctx, toggle: discord.Option(bool) or None = None):
        if toggle is not None:
            self.songRepeat[ctx.guild.id] = toggle
        return await ctx.respond(
            f':repeat_one: **單曲循環**  {":white_check_mark: " if self.songRepeat[ctx.guild.id] else ":x:"}')

    # & loop
    @music.command(name="loop")
    @_is_author_in_vc()
    async def music_loop(self, ctx, toggle: discord.Option(bool) or None = None):
        if toggle is not None:
            self.queueLoop[ctx.guild.id] = toggle
        return await ctx.respond(
            f':repeat: **歌單循環**  {":white_check_mark: " if self.queueLoop[ctx.guild.id] else ":x:"}')

    # & skip
    @music.command(name="skip")
    @_is_author_in_vc()
    @_is_bot_joined()
    async def music_skip(self, ctx):
        player = self.get_player(ctx.guild)
        await player.stop()
        return await ctx.respond(":fast_forward: Skipped")

    # & quickplay
    # TODO quickplay system

    # & play
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @music.command(name="play", description='放音樂')
    @_is_author_in_vc()
    async def music_play(self, ctx, search: discord.Option(str, description='請搜尋') or None = None):
        player = self.get_player(ctx.guild)

        if search is None:
            if player.is_paused():
                await player.resume()
                return await ctx.respond("Unpause!")
            else:
                raise commands.CommandError("missing_song_name")

        searched_tracklist = await wavelink.YouTubeTrack.search(search)

        if player is None:
            await ctx.author.voice.channel.connect(cls=wavelink.Player)

        await ctx.respond(f":musical_note: **Searching** :mag_right: {search}")
        if yarl.URL(search).is_absolute():

            await self.add_track(searched_tracklist[0], ctx)
        else:
            await ctx.respond(view=self._View(ctx, searched_tracklist))

    class _View(discord.ui.View):
        def __init__(self, ctx, tracks):
            super().__init__(timeout=60)
            self.ctx = ctx
            self.add_item(self._Menu(tracks))

        # async def on_timeout(self) -> None:
        #     await MusicCmd.add_track('timeout', self.ctx)

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
                    await MusicCmd.add_track('cancel', interaction)
                for track in self.tracks:
                    if track.identifier == self.values[0]:
                        await MusicCmd.add_track(track, interaction)
                        return

    @classmethod
    async def add_track(cls, track, context):
        player = cls.get_player(context.guild)

        if isinstance(context, discord.Interaction):

            if track == 'cancel':
                await context.response.edit_message(content='搜尋已取消', view=None)
            else:
                await context.response.edit_message(content=f'已將 **{escape_markdown(track.title)}** 加入播放清單中', view=None)
        elif isinstance(context, discord.commands.context.ApplicationContext):
            if track == 'timeout':
                await context.edit(content='給林北認真選啦', view=None)
            else:
                await context.respond(content=f'已將 **{escape_markdown(track.title)}** 加入播放清單中')

        if isinstance(track, wavelink.Track):
            await player.queue.put_wait(track)
        if not player.is_playing():
            await cls._play(context.guild)

    @classmethod
    async def _play(cls, guild):
        player = cls.get_player(guild)
        np = await player.queue.get_wait()
        logging.getLogger(f"DiscordMusicBot.Guild.{player.guild}").info(
            f"Now playing: '{np}'", extra={'classname': __name__})
        await player.play(np)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        logger = logging.getLogger(f'DiscordMusicBot.Guild.{player.guild}')
        logger.info(
            f"Finished playing: {escape_markdown(track.title)} [{reason}]", extra={'classname': __name__})

        match reason:
            case "LOAD_FAILED":
                logger.warning("無法載入歌曲！")

            case "STOPPED":
                pass

            case _:
                if self.songRepeat[player.guild.id]:
                    player.queue.put_at_front(track)
                elif self.queueLoop[player.guild.id]:
                    player.queue.put(track)

        await self._play(player.guild)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
