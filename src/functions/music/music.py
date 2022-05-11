import logging
from typing import Optional

import discord
import wavelink
import yarl
from discord.commands import SlashCommandGroup
from discord.ext import commands
from wavelink import YouTubePlaylist


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
                                            host="aitronlavalink.tk",
                                            port=443,
                                            password="aitronbots.tk",
                                            https=True)

        try:
            wavelink.NodePool.get_node()
            logging.getLogger('DiscordMusicBot').info(
                "Lavalink server connected")
        except wavelink.errors.ZeroConnectedNodes:
            logging.getLogger('DiscordMusicBot').error(
                "Fails to connect lavalink server!")

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.songRepeat[guild.id] = False
            self.queueLoop[guild.id] = False

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

    @classmethod
    def get_node(cls):
        node = wavelink.NodePool.get_node()
        return node

    @classmethod
    def get_player(cls, ctx):
        node = cls.get_node()
        player: wavelink.Player = node.get_player(ctx.guild)
        return player

    music = SlashCommandGroup("music", "音樂用")

    # & join
    @music.command(name="join")
    @_is_author_in_vc()
    async def music_join(self, ctx):

        player = self.get_player(ctx)

        if player is None:
            await ctx.respond(":heart: 我要進來嘍~ :heart:")
            await ctx.author.voice.channel.connect(cls=wavelink.Player)

        elif player.channel.id == ctx.author.voice.channel.id:
            await ctx.respond(":rage: 你已經有一個了！ :middle_finger:")
            return

        else:
            await ctx.respond(":two_hearts: 我來啦~ :cupid:")
            await player.move_to(ctx.author.voice.channel)

        logging.getLogger(f'DiscordMusicBot.Guild.{ctx.guild}').debug(
            f'joined channel<{ctx.author.voice.channel}>')
        return

    # & leave
    @music.command(name="leave")
    @_is_author_in_vc()
    async def music_leave(self, ctx):

        player = self.get_player(ctx)
        if player is None:
            await ctx.respond(":question:???:exclamation:")
            return
        await player.disconnect()
        await ctx.respond(":broken_heart: Ok bye... :broken_heart:")

    # & pause
    @music.command(name="pause")
    @_is_author_in_vc()
    async def music_pause(self, ctx):

        player = self.get_player(ctx)
        if player.is_playing():
            await player.pause()
        await ctx.respond("paused")

    # & nowplaying
    @music.command(name="nowplaying")
    async def music_nowplaying(self, ctx):
        player = self.get_player(ctx)
        if player is None or player.source is None:
            return await ctx.respond(f':sleeping: 閒置中...')
        else:
            return await ctx.respond(f':musical_note: 現正播放:\n**{player.source.title}**')

    # & queue

    @music.command(name="queue")
    @_is_author_in_vc()
    async def music_queue(self, ctx):
        player = self.get_player(ctx)

        number_map = {"1": ":one:", "2": ":two:", "3": ":three:", "4": ":four:",
                      "5": ":five:", "6": ":six:", "7": ":seven:", "8": ":eight:", "9": ":nine:", "0": ":zero:"}

        i: int = 0
        index = str
        respond_str = [
            '' if player.source is None or player is None else f":musical_note: 現正播放:\n**{player.source.title}**", '',
            ':notes: 歌單:']
        for song in player.queue:
            i = i + 1
            if 10 <= i <= 99:
                index = str(i)
            elif 1 <= i <= 9:
                index = "0" + str(i)

            respond_str.append(
                f'{"".join([number_map[a] for a in list(index)])}  {song.title}')
        respond_str.append(f'')
        respond_str.append(
            f':repeat_one: **單曲循環**  {":white_check_mark: " if self.songRepeat[ctx.guild.id] else ":x:"}')
        respond_str.append(
            f':repeat: **歌單循環**  {":white_check_mark: " if self.queueLoop[ctx.guild.id] else ":x:"}')

        return await ctx.respond('\n'.join(respond_str))

    # & clear
    @music.command(name="clear")
    @_is_author_in_vc()
    async def music_clear(self, ctx):
        player = self.get_player(ctx)
        if player.queue.is_empty:
            pass
        else:
            player.queue.clear()

    # & repeat
    @music.command(name="repeat")
    @_is_author_in_vc()
    async def music_repeat(self, ctx):
        self.songRepeat[ctx.guild.id] = not self.songRepeat[ctx.guild.id]
        return await ctx.respond(f":repeat_one: **已{f'啟用' if self.songRepeat[ctx.guild.id] else f'禁用'}單曲循環**")

    # & loop
    @music.command(name="loop")
    @_is_author_in_vc()
    async def music_loop(self, ctx):
        self.queueLoop[ctx.guild.id] = not self.queueLoop[ctx.guild.id]
        return await ctx.respond(f":repeat_one: **已{f'啟用' if self.queueLoop[ctx.guild.id] else f'禁用'}歌單循環**")

    # & skip
    @music.command(name="skip")
    @_is_author_in_vc()
    @_is_bot_joined()
    async def music_skip(self, ctx):
        player = self.get_player(ctx)
        await player.stop()
        return await ctx.respond("skipped")

    class MusicPlayer:
        def __init__(self, ):
            self._menu: Optional[discord.ui.Select] = None
            self.ctx = None
            self.searched_tracklist: Optional[list[wavelink.Track]] = None
            self.view: Optional[discord.ui.View] = None

        async def _select_menu_callback(self, interaction):
            self.view.clear_items()
            for i in self.searched_tracklist:
                if i.info['identifier'] == self._menu.values[0]:
                    self.selected_track = i
                    break
            await self.add_track(self.selected_track)
            await interaction.response.send_message(f'已將 {self.selected_track.title} 加入播放清單中')

        async def add_track(self, track):
            player = MusicCmd.get_player(self.ctx)

            await player.queue.put_wait(track)

            if not player.is_playing():
                await self.play()

        async def create_task(self, ctx, search):
            self.ctx = ctx
            self.searched_tracklist = await wavelink.YouTubeTrack.search(search)
            self._menu = discord.ui.Select(placeholder="為啥你不要直接輸入網址呢？")
            self._menu.callback = self._select_menu_callback

            for track in self.searched_tracklist:
                self._menu.add_option(
                    label=track.info['title'], value=track.info['identifier'])
            self.view = discord.ui.View(timeout=30)
            self.view.add_item(self._menu)
            await ctx.respond(f":musical_note: **Searching** :mag_right: {search}", view=self.view, ephemeral=True)

        async def play(self):
            player = MusicCmd.get_player(self.ctx)
            np = await player.queue.get_wait()
            logging.getLogger(f"DiscordMusicBot.Guild.{self.ctx.guild}").debug(
                f"Now playing: '{np}'")
            await player.play(np)

    mp = MusicPlayer()

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        logging.getLogger(f'DiscordMusicBot.Guild.{player.guild}').debug(
            f"Track '{track}' finished playing: {reason}")
        if reason == "LOAD_FAILED":
            raise commands.CommandError("無法載入歌曲！")
        if self.songRepeat[player.guild.id]:
            player.queue.put_at_front(track)
        elif self.queueLoop[player.guild.id]:
            player.queue.put(track)

        await self.mp.play()

    # & play
    @music.command(name="play", description='放音樂')
    @_is_author_in_vc()
    @_is_bot_joined()
    async def music_play(self, ctx, search: discord.Option(str, description='請搜尋') or None = None):

        player = self.get_player(ctx)

        if search is None:
            if player.is_paused():
                await player.resume()
                return await ctx.respond("Unpause!")
            else:
                raise commands.CommandError("missing_song_name")

        parsed_url = yarl.URL(search)

        await self.mp.create_task(ctx, search)
        if parsed_url.is_absolute() and (str(parsed_url.host) == 'youtube.com' or str(
                parsed_url.host) == 'www.youtube.com'):
            await self.mp.add_track(await self.get_node().get_playlist(cls=YouTubePlaylist, identifier=search))
