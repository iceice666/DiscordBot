import logging
import time
import wavelink

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.utils import escape_markdown


from .player import _PLAYER
from ... import config


class MusicCmd(commands.Cog):

    def __init__(self, bot):

        self._menu = None
        self.bot = bot

        self.song_repeat: dict[int, bool] = {}
        self.queue_loop: dict[int, bool] = {}

        self.remove_after_skip: dict[int, bool] = {}

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
            self.song_repeat[guild.id] = False
            self.queue_loop[guild.id] = False
            self.remove_after_skip[guild.id] = False

    @staticmethod
    def get_node():
        node = wavelink.NodePool.get_node()
        return node

    @staticmethod
    def get_player(guild):
        player: wavelink.Player = wavelink.NodePool.get_node().get_player(guild)
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
    @music.command(name="nowplaying")
    async def music_nowplaying(self, ctx):
        player = self.get_player(ctx.guild)

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
            f':repeat_one: **單曲循環**  {":white_check_mark: " if self.song_repeat[ctx.guild.id] else ":x:"}')
        respond_str.append(
            f':repeat: **歌單循環**  {":white_check_mark: " if self.queue_loop[ctx.guild.id] else ":x:"}')

        return await ctx.respond('\n'.join(respond_str))

    # & remove
    @music.command(name="remove")
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
                    player = MusicCmd.get_player(interaction.guild)
                    track_title = player.queue._queue[self.track_index].title
                    player.queue._queue.remove(
                        player.queue._queue[self.track_index])
                    await interaction.response.edit_message(content=f'已刪除 **{track_title}**', view=None)

        player = self.get_player(ctx.guild)
        if by_index is not None:
            return await ctx.respond(content=f'刪除 {player.queue._queue[self.track_index].title} ?',
                                     view=_Remove(track_index=by_index-1))
        elif by_index is None:
            return await ctx.respond(view=_Selection(player.queue._queue))

    # & clear

    @music.command(name="clear")
    @_is_author_in_vc()
    async def music_clear(self, ctx):
        player = self.get_player(ctx.guild)
        if not player.queue.is_empty:
            player.queue.clear()

    # & repeat
    @music.command(name="repeat")
    @_is_author_in_vc()
    async def music_repeat(self, ctx, toggle: discord.Option(bool) or None = None):
        if toggle is not None:
            self.song_repeat[ctx.guild.id] = toggle
        return await ctx.respond(
            f':repeat_one: **單曲循環**  {":white_check_mark: " if self.song_repeat[ctx.guild.id] else ":x:"}')

    # & loop
    @music.command(name="loop")
    @_is_author_in_vc()
    async def music_loop(self, ctx, toggle: discord.Option(bool) or None = None):
        if toggle is not None:
            self.queue_loop[ctx.guild.id] = toggle
        return await ctx.respond(
            f':repeat: **歌單循環**  {":white_check_mark: " if self.queue_loop[ctx.guild.id] else ":x:"}')

    # & skip
    @music.command(name="skip")
    @_is_author_in_vc()
    @_is_bot_joined()
    async def music_skip(self, ctx,
                         remove: discord.Option(bool, description="是否要在跳過後將歌曲重清單移除") or None = None):

        class _Remove(discord.ui.View):
            def __init__(self, remove_after_skip):
                super().__init__(timeout=10)
                self.add_item(self._Cancel())
                self.add_item(self._Confirm())
                self.remove_after_skip = remove_after_skip

            async def on_timeout(self) -> None:
                await super().on_timeout()

            class _Cancel(discord.ui.Button):
                def __init__(self, remove_after_skip):
                    super().__init__(label="No",  style=discord.ButtonStyle.primary)
                    self.remove_after_skip = remove_after_skip

                async def callback(self,  interaction):
                    player = MusicCmd.get_player(interaction.guild)
                    self.remove_after_skip[ctx.guild.id] = False
                    await player.stop()
                    await interaction.response.edit_message(content=':fast_forward: 已跳過', view=None)

            class _Confirm(discord.ui.Button):
                def __init__(self, remove_after_skip):
                    super().__init__(label="Yes", style=discord.ButtonStyle.danger)
                    self.remove_after_skip = remove_after_skip

                async def callback(self,  interaction):
                    player = MusicCmd.get_player(interaction.guild)
                    self.remove_after_skip[ctx.guild.id] = True
                    await player.stop()
                    await interaction.response.edit_message(content=f':fast_forward: 已跳過', view=None)

        player = self.get_player(ctx.guild)

        if remove is None:
            if player.source.duration > 600:
                await ctx.respond("是否要在跳過後將歌曲重清單移除", view=_Remove(self.remove_after_skip))
            else:
                await player.stop()
                await ctx.respond(":fast_forward: 已跳過")
        else:
            self.remove_after_skip[ctx.guild.id] = True
            await player.stop()

    # & quickplay
    # TODO quickplay system
    async def music_quickplay(self, ctx):
        pass

    # & play
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    _player = _PLAYER()

    @music.command(name="play", description='放音樂')
    @_is_author_in_vc()
    async def music_play(self, ctx, search: discord.Option(str, description='請搜尋') or None = None):
        await self._player._run(ctx, search)

    @commands.Cog.listener('on_wavelink_track_end')
    async def _playing_finished(self, player, track, reason):
        logger = logging.getLogger(f'DiscordBot.Guild.{player.guild}')
        logger.info(
            f"Finished playing: {escape_markdown(track.title)} [{reason}]", extra={'classname': __name__})

        match reason:
            case "LOAD_FAILED":
                logger.warning("無法載入歌曲！")
                commands.CommandError("**無法載入歌曲！**\n**請重新加入歌單！**")

            case "STOPPED" if self.remove_after_skip[player.guild.id]:
                self.remove_after_skip[player.guild.id] = False

            case _ if not self.remove_after_skip[player.guild.id]:
                if self.song_repeat[player.guild.id]:
                    player.queue.put_at_front(track)
                elif self.queue_loop[player.guild.id]:
                    player.queue.put(track)
                self.remove_after_skip[player.guild.id] = False

                await self._player._play(player.guild)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
