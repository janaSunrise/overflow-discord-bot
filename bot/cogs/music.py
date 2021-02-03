import asyncio
import copy
import datetime
import math
import random
import re
import textwrap
import typing as t

import async_timeout
import discord
from discord.ext import commands, menus
import spotify
import wavelink
import yarl

from bot import config
from bot.utils.errors import IncorrectChannelError, InvalidRepeatMode, NoChannelProvided
from bot.utils.utils import format_time

# URL matching REGEX.
TIME_REG = re.compile("[0-9]+")
URL_REG = re.compile(r'https?://(?:www\.)?.+')
SPOTIFY_URL_REG = re.compile(r'https?://open.spotify.com/(?P<type>album|playlist|track)/(?P<id>[a-zA-Z0-9]+)')


class Track(wavelink.Track):
    """Wavelink Track object with a requester attribute."""
    __slots__ = ('requester',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get('requester')


class Player(wavelink.Player):
    """Custom wavelink player class."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.context: commands.Context = kwargs.get('context', None)
        if self.context:
            self.dj: discord.Member = self.context.author

        self.queue = asyncio.Queue()
        self.controller = None

        self.waiting = False
        self.updating = False

        self.clear_votes = set()
        self.pause_votes = set()
        self.resume_votes = set()
        self.skip_votes = set()
        self.shuffle_votes = set()
        self.stop_votes = set()

    async def do_next(self) -> None:
        if self.is_playing or self.waiting:
            return

        # Clear the votes for a new song.
        self.clear_votes.clear()
        self.pause_votes.clear()
        self.resume_votes.clear()
        self.skip_votes.clear()
        self.shuffle_votes.clear()
        self.stop_votes.clear()

        try:
            self.waiting = True
            with async_timeout.timeout(300):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            # No music has been played for 5 minutes, cleanup and disconnect.
            return await self.teardown()

        await self.play(track)
        self.waiting = False

        # Invoke our players controller.
        await self.invoke_controller()

    async def invoke_controller(self) -> None:
        """Method which updates or sends a new player controller."""
        if self.updating:
            return
        self.updating = True

        if not self.controller:
            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.context)

        elif not await self.is_position_fresh():
            try:
                await self.controller.message.delete()
            except discord.HTTPException:
                pass

            self.controller.stop()

            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.context)

        else:
            embed = self.build_embed()
            await self.controller.message.edit(content=None, embed=embed)

        self.updating = False

    def build_embed(self) -> t.Optional[discord.Embed]:
        """Method which builds our players controller embed."""
        track = self.current
        if not track:
            return

        channel = self.bot.get_channel(int(self.channel_id))
        qsize = self.queue.qsize()

        embed = discord.Embed(title=f'Let\'s Listen to Music 🎵 | {channel.name}', colour=discord.Color.blurple())
        embed.description = f'Now Playing:\n**`{track.title}`**\n\n'
        embed.set_thumbnail(url=track.thumb)

        embed.add_field(name='Duration', value=str(datetime.timedelta(milliseconds=int(track.length))))
        embed.add_field(name='Queue Length', value=str(qsize))
        embed.add_field(name='Volume', value=f'**`{self.volume}%`**')
        embed.add_field(name='Requested By', value=track.requester.mention)
        embed.add_field(name='DJ', value=self.dj.mention)
        embed.add_field(name='Video URL', value=f'[Click Here!]({track.uri})')

        return embed

    async def is_position_fresh(self) -> bool:
        """Method which checks whether the player controller should be remade or updated."""
        try:
            async for message in self.context.channel.history(limit=5):
                if message.id == self.controller.message.id:
                    return True
        except (discord.HTTPException, AttributeError):
            return False

        return False

    async def teardown(self):
        """Clear internal states, remove player controller and disconnect."""
        try:
            await self.controller.message.delete()
        except discord.HTTPException:
            pass

        self.controller.stop()

        try:
            await self.destroy()
        except KeyError:
            pass


class InteractiveController(menus.Menu):
    """The Players interactive controller menu class."""
    def __init__(self, *, embed: discord.Embed, player: Player):
        super().__init__(timeout=None)

        self.embed = embed
        self.player = player

    def update_context(self, payload: discord.RawReactionActionEvent):
        """Update our context with the user who reacted."""
        ctx = copy.copy(self.ctx)
        ctx.author = payload.member
        return ctx

    def reaction_check(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == 'REACTION_REMOVE':
            return False

        if not payload.member:
            return False

        if payload.member.bot:
            return False

        if payload.message_id != self.message.id:
            return False

        if payload.member not in self.bot.get_channel(int(self.player.channel_id)).members:
            return False

        return payload.emoji in self.buttons

    async def send_initial_message(self, ctx: commands.Context, channel: discord.TextChannel) -> discord.Message:
        return await channel.send(embed=self.embed)

    @menus.button(emoji='\u25B6')
    async def resume_command(self, payload: discord.RawReactionActionEvent):
        """Resume button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('resume')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23F8')
    async def pause_command(self, payload: discord.RawReactionActionEvent):
        """Pause button"""
        ctx = self.update_context(payload)

        command = self.bot.get_command('pause')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23F9')
    async def stop_command(self, payload: discord.RawReactionActionEvent):
        """Stop button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('stop')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u23ED')
    async def skip_command(self, payload: discord.RawReactionActionEvent):
        """Skip button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('skip')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\U0001F500')
    async def shuffle_command(self, payload: discord.RawReactionActionEvent):
        """Shuffle button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('shuffle')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u2795')
    async def volup_command(self, payload: discord.RawReactionActionEvent):
        """Volume up button"""
        ctx = self.update_context(payload)

        command = self.bot.get_command('vol_up')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\u2796')
    async def voldown_command(self, payload: discord.RawReactionActionEvent):
        """Volume down button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('vol_down')
        ctx.command = command

        await self.bot.invoke(ctx)

    @menus.button(emoji='\U0001F1F6')
    async def queue_command(self, payload: discord.RawReactionActionEvent):
        """Player queue button."""
        ctx = self.update_context(payload)

        command = self.bot.get_command('queue')
        ctx.command = command

        await self.bot.invoke(ctx)


class PaginatorSource(menus.ListPageSource):
    """Player queue paginator class."""
    def __init__(self, entries, *, per_page=8):
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = discord.Embed(title='Coming Up...', colour=0x4f0321)
        embed.description = '\n'.join(f'`{index}. {title}`' for index, title in enumerate(page, 1))
        return embed

    def is_paginating(self) -> bool:
        return True


class Music(commands.Cog, wavelink.WavelinkMixin):
    """Music Cog."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):
            bot.wavelink = wavelink.Client(bot=bot)

        bot.loop.create_task(self.start_nodes())

    async def start_nodes(self) -> None:
        """Connect and initiate nodes."""
        await self.bot.wait_until_ready()

        if self.bot.wavelink.nodes:
            previous = self.bot.wavelink.nodes.copy()

            for node in previous.values():
                await node.destroy()

        for node in config.nodes.values():
            await self.bot.wavelink.initiate_node(**node)

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        print(f'Node {node.identifier} is ready!')

    @wavelink.WavelinkMixin.listener('on_track_stuck')
    @wavelink.WavelinkMixin.listener('on_track_end')
    @wavelink.WavelinkMixin.listener('on_track_exception')
    async def on_player_stop(self, node: wavelink.Node, payload):
        await payload.player.do_next()

    @commands.Cog.listener()
    async def on_voice_state_update(
            self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ) -> None:
        if member.bot:
            return

        player: Player = self.bot.wavelink.get_player(member.guild.id, cls=Player)

        if not player.channel_id or not player.context:
            player.node.players.pop(member.guild.id)
            return

        channel = self.bot.get_channel(int(player.channel_id))

        if member == player.dj and after.channel is None:
            for mem in channel.members:
                if mem.bot:
                    continue
                else:
                    player.dj = mem
                    return
        elif after.channel == channel and player.dj not in channel.members:
            player.dj = member

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        """Cog wide error handler."""
        if isinstance(error, IncorrectChannelError):
            return

        if isinstance(error, NoChannelProvided):
            return await ctx.send('You must be in a voice channel or provide one to connect to.')

    async def cog_check(self, ctx: commands.Context):
        """Cog wide check, which disallows commands in DMs."""
        if not ctx.guild:
            await ctx.send('Music commands are not available in Private Messages.')
            return False

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        """
        Coroutine called before command invocation.

        We mainly just want to check whether the user is in the players controller channel.
        """
        player: Player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player, context=ctx)

        if player.context:
            if player.context.channel != ctx.channel:
                await ctx.send(
                    embed=discord.Embed(
                        description=f'{ctx.author.mention}, you must be in {player.context.channel.mention} for this session.',
                        color=discord.Color.red()
                    )
                )
                raise IncorrectChannelError

        if ctx.command.name in ['connect',  'play', 'equalizer', 'volume', 'repeat'] and not player.context:
            return
        elif self.is_privileged(ctx):
            return

        if not player.channel_id:
            return

        channel = self.bot.get_channel(int(player.channel_id))
        if not channel:
            return

        if player.is_connected:
            if ctx.author not in channel.members:
                await ctx.send(
                    embed=discord.Embed(
                        description=f'{ctx.author.mention}, you must be in `{channel.name}` to use voice commands.',
                        color=discord.Color.red()
                    )
                )
                raise IncorrectChannelError

    def required(self, ctx: commands.Context):
        """Method which returns required votes based on amount of members in a channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)
        channel = self.bot.get_channel(int(player.channel_id))
        required = math.ceil((len(channel.members) - 1) / 2.5)

        if ctx.command.name in ["stop", "skip"]:
            if len(channel.members) == 3:
                required = 2
        return required

    def is_privileged(self, ctx: commands.Context):
        """Check whether the user is an Admin or DJ."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        return player.dj == ctx.author or ctx.author.guild_permissions.kick_members

    @commands.command()
    async def connect(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Connect to a voice channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_connected:
            return

        channel = getattr(ctx.author.voice, 'channel', channel)
        if channel is None:
            raise NoChannelProvided

        await player.connect(channel.id)

    @commands.command(aliases=["leave"])
    async def disconnect(self, ctx: commands.Context):
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        await player.teardown()
        await ctx.send(
            embed=discord.Embed(description="Successfully disconnected.", color=discord.Color.green())
        )

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        """Play or queue a song with the given query."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            await ctx.invoke(self.connect)

        spotify_url_check = SPOTIFY_URL_REG.match(query)

        if not spotify_url_check:
            url = yarl.URL(query)

            if not url.scheme or not url.host:
                if "soundcloud" in query:
                    query = f'scsearch:{query}'
                else:
                    query = f'ytsearch:{query}'

            tracks = await self.bot.wavelink.get_tracks(query)
            if not tracks:
                return await ctx.send('No songs were found with that query. Please try again.', delete_after=15)

            if isinstance(tracks, wavelink.TrackPlaylist):
                for track in tracks.tracks:
                    track = Track(track.id, track.info, requester=ctx.author)
                    await player.queue.put(track)

                print(tracks)
                await ctx.send(
                    embed=discord.Embed(
                        description=textwrap.dedent(f"""
                        ```ini
                        Added the playlist {tracks.data["playlistInfo"]["name"]} with {len(tracks.tracks)} songs to the 
                        queue.
                        ```
                        """),
                        color=discord.Color.blurple()
                    ),
                    delete_after=15
                )
            else:
                track = Track(tracks[0].id, tracks[0].info, requester=ctx.author)
                await ctx.send(
                    embed=discord.Embed(
                        description=f'```ini\nAdded {track.title} to the Queue\n```',
                        color=discord.Color.blurple()
                    ),
                    delete_after=15
                )
                await player.queue.put(track)
        else:
            search_tracks = None

            search_type = spotify_url_check.group('type')
            spotify_id = spotify_url_check.group('id')

            try:
                if search_type == 'album':
                    search_result = await self.bot.spotify.get_album(spotify_id=spotify_id)
                    search_tracks = await search_result.get_all_tracks()
                elif search_type == 'playlist':
                    search_result = spotify.Playlist(
                        client=self.bot.spotify_client,
                        data=await self.bot.spotify_http.get_playlist(spotify_id)
                    )
                    search_tracks = await search_result.get_all_tracks()
                elif search_type == 'track':
                    search_result = await self.bot.spotify.get_track(spotify_id=spotify_id)
                    search_tracks = [search_result]
            except spotify.NotFound or discord.HTTPException:
                return await ctx.send(f'No results were found for your Spotify link.', delete_after=15)

            if not search_tracks:
                return await ctx.send('No songs were found with that query. Please try again.', delete_after=15)

            tracks = [
                wavelink.Track(
                    id_='',
                    info={
                        'title': track.name or 'Unknown',
                        'author': ', '.join(artist.name for artist in track.artists) or 'Unknown',
                        'length': track.duration or 0,
                        'identifier': track.id or 'Unknown',
                        'uri': track.url or 'spotify',
                        'isStream': False,
                        'isSeekable': False,
                        'position': 0,
                        'thumbnail': track.images[0].url if track.images else None
                    },
                ) for track in search_tracks
            ]

        if not player.is_playing:
            await player.do_next()

    @commands.command()
    async def pause(self, ctx: commands.Context):
        """Pause the currently playing song."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_paused or not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send(
                embed=discord.Embed(
                    description='An admin or DJ has paused the player.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )
            await ctx.message.add_reaction('⏯')
            player.pause_votes.clear()

            return await player.set_pause(True)

        required = self.required(ctx)
        player.pause_votes.add(ctx.author)

        if len(player.pause_votes) >= required:
            await ctx.send(
                embed=discord.Embed(
                    description='Vote to pause passed. Pausing player.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )
            await ctx.message.add_reaction('⏯')
            player.pause_votes.clear()
            await player.set_pause(True)
        else:
            await ctx.send(
                embed=discord.Embed(
                    description=f'{ctx.author.mention} has voted to pause the player.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )

    @commands.command()
    async def resume(self, ctx: commands.Context):
        """Resume a currently paused player."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_paused or not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send(
                embed=discord.Embed(
                    description='An admin or DJ has resumed the player.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )
            await ctx.message.add_reaction('⏯')
            player.resume_votes.clear()

            return await player.set_pause(False)

        required = self.required(ctx)
        player.resume_votes.add(ctx.author)

        if len(player.resume_votes) >= required:
            await ctx.send(
                embed=discord.Embed(
                    description='Vote to resume passed. Resuming player.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )
            await ctx.message.add_reaction('⏯')
            player.resume_votes.clear()
            await player.set_pause(False)
        else:
            await ctx.send(
                embed=discord.Embed(
                    description=f'{ctx.author.mention} has voted to resume the player.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )

    @commands.command()
    async def seek(self, ctx: commands.Context, *, time: str) -> None:
        """Seek to a given position in a track."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        raw_seconds = TIME_REG.search(time)
        if not raw_seconds:
            await ctx.send(
                embed=discord.Embed(
                    description="You need to specify the amount of seconds to skip!",
                    color=discord.Color.red()
                )
            )
            return

        seconds = int(raw_seconds.group()) * 1000

        if time.startswith("-"):
            seconds *= -1

        track_time = player.position + seconds
        await player.seek(track_time)

        await ctx.send(
            embed=discord.Embed(
                description=f"Moved track to **{format_time(track_time)}**",
                color=discord.Color.green()
            )
        )

    @commands.command()
    async def repeat(self, ctx, mode: str):
        """
        Repeat one or more songs.

        **MODES**:
        - `none` (stop repeat)
        - `1`
        - `all`
        """
        if mode not in ("none", "1", "all"):
            raise InvalidRepeatMode

        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        player.queue.set_repeat_mode(mode)
        await ctx.send(
            embed=discord.Embed(
                description=f"The repeat mode has been set to {mode}.",
                color=discord.Color.green()
            )
        )

    @commands.command()
    async def skip(self, ctx: commands.Context):
        """Skip the currently playing song."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send(
                embed=discord.Embed(
                    description='An admin or DJ has skipped the song.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )
            await ctx.message.add_reaction('⏭')
            player.skip_votes.clear()

            return await player.stop()

        if ctx.author == player.current.requester:
            await ctx.send(
                embed=discord.Embed(
                    description='The song requester has skipped the song.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )
            await ctx.message.add_reaction('⏭')
            player.skip_votes.clear()

            return await player.stop()

        required = self.required(ctx)
        player.skip_votes.add(ctx.author)

        if len(player.skip_votes) >= required:
            await ctx.send(
                embed=discord.Embed(
                    description='Vote to skip passed. Skipping song.',
                    color=discord.Color.green()
                ),
                delete_after=10
            )
            player.skip_votes.clear()
            await player.stop()
        else:
            await ctx.send(
                embed=discord.Embed(
                    description=f'{ctx.author.mention} has voted to skip the song.',
                    color=discord.Color.gold()
                ),
                delete_after=15
            )

    @commands.command()
    async def stop(self, ctx: commands.Context):
        """Stop the player and clear all internal states."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if self.is_privileged(ctx):
            await ctx.send(
                embed=discord.Embed(
                    description='An admin or DJ has stopped the player.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )
            await ctx.message.add_reaction('⏹')
            return await player.teardown()

        required = self.required(ctx)
        player.stop_votes.add(ctx.author)

        if len(player.stop_votes) >= required:
            await ctx.send(
                embed=discord.Embed(
                    description='Vote to stop passed. Stopping the player.',
                    color=discord.Color.green()
                ),
                delete_after=10
            )
            await ctx.message.add_reaction('⏹')
            await player.teardown()
        else:
            await ctx.send(
                embed=discord.Embed(
                    description=f'{ctx.author.mention} has voted to stop the player.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx: commands.Context, *, vol: int):
        """Change the players volume, between 1 and 100."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            await ctx.send(
                embed=discord.Embed(
                    description='Only the DJ or admins may change the volume.',
                    color=discord.Color.red()
                ),
                delete_after=10
            )
            return

        if not 0 < vol < 101:
            await ctx.send(
                embed=discord.Embed(
                    description='Please enter a value between 1 and 100.',
                    color=discord.Color.red()
                ),
                delete_after=10
            )
            return

        await player.set_volume(vol)
        await ctx.send(
            embed=discord.Embed(
                description=f'Set the volume to **{vol}**%',
                color=discord.Color.green()
            ),
            delete_after=10
        )

    @commands.command(aliases=['mix'])
    async def shuffle(self, ctx: commands.Context):
        """Shuffle the players queue."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if player.queue.qsize() < 3:
            await ctx.send(
                embed=discord.Embed(
                    description='Add more songs to the queue before shuffling.',
                    color=discord.Color.red()
                ),
                delete_after=15
            )
            return

        if self.is_privileged(ctx):
            await ctx.send(
                embed=discord.Embed(
                    description='An admin or DJ has shuffled the playlist.',
                    color=discord.Color.gold()
                ),
                delete_after=10
            )
            player.shuffle_votes.clear()
            return random.shuffle(player.queue._queue)

        required = self.required(ctx)
        player.shuffle_votes.add(ctx.author)

        if len(player.shuffle_votes) >= required:
            await ctx.send(
                embed=discord.Embed(
                    description='Vote to shuffle passed. Shuffling the playlist.',
                    color=discord.Color.green()
                ),
                delete_after=10
            )
            player.shuffle_votes.clear()
            random.shuffle(player.queue._queue)
        else:
            await ctx.send(
                embed=discord.Embed(
                    description=f'{ctx.author.mention} has voted to shuffle the playlist.',
                    color=discord.Color.gold()
                ),
                delete_after=15
            )

    @commands.command(hidden=True)
    async def vol_up(self, ctx: commands.Context):
        """Command used for volume up button."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected or not self.is_privileged(ctx):
            return

        vol = int(math.ceil((player.volume + 10) / 10)) * 10

        if vol > 100:
            vol = 100
            await ctx.send(
                embed=discord.Embed(
                    description='Maximum volume reached',
                    color=discord.Color.red()
                ),
                delete_after=10
            )

        await player.set_volume(vol)

    @commands.command(hidden=True)
    async def vol_down(self, ctx: commands.Context):
        """Command used for volume down button."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected or not self.is_privileged(ctx):
            return

        vol = int(math.ceil((player.volume - 10) / 10)) * 10

        if vol < 0:
            vol = 0
            await ctx.send(
                embed=discord.Embed(
                    description='Player is currently muted',
                    color=discord.Color.red()
                ),
                delete_after=10
            )

        await player.set_volume(vol)

    @commands.command(aliases=['eq'])
    async def equalizer(self, ctx: commands.Context, *, equalizer: str):
        """Change the players equalizer."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            await ctx.send(
                embed=discord.Embed(
                    description='Only the DJ or admins may change the equalizer.',
                    color=discord.Color.red()
                )
            )

        eqs = {
            'flat': wavelink.Equalizer.flat(),
            'boost': wavelink.Equalizer.boost(),
            'metal': wavelink.Equalizer.metal(),
            'piano': wavelink.Equalizer.piano()
        }

        eq = eqs.get(equalizer.lower(), None)

        if not eq:
            joined = "\n".join(eqs.keys())
            await ctx.send(
                embed=discord.Embed(
                    description=f'Invalid EQ provided. Valid EQs:\n\n{joined}',
                    color=discord.Color.red()
                )
            )
            return

        await ctx.send(
            embed=discord.Embed(
                description=f'Successfully changed equalizer to {equalizer}',
                color=discord.Color.red()
            ),
            delete_after=15
        )
        await player.set_eq(eq)

    @commands.command(aliases=['q', 'que'])
    async def queue(self, ctx: commands.Context):
        """Display the players queued songs."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if player.queue.qsize() == 0:
            await ctx.send(
                embed=discord.Embed(
                    description='There are no more songs in the queue.',
                    color=discord.Color.red()
                ),
                delete_after=15
            )
            return

        entries = [track.title for track in player.queue._queue]
        pages = PaginatorSource(entries=entries)
        paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)

        await paginator.start(ctx)

    @commands.command(aliases=['np', 'now_playing', 'current'])
    async def nowplaying(self, ctx: commands.Context):
        """Update the player controller."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        await player.invoke_controller()

    @commands.command(aliases=["clear-queue", "clear-q"])
    async def clear_queue(self, ctx: commands.Context):
        """Clear the songs from the queue."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if self.is_privileged(ctx) or ctx.author == player.current.requester:
            if player.is_playing:
                while player.is_playing:
                    await player.stop()

                return await ctx.send(
                    embed=discord.Embed(
                        description="Cleared the queue!",
                        color=discord.Color.green()
                    ),
                    delete_after=10
                )
            else:
                return await ctx.send(
                    embed=discord.Embed(
                        description="Nothing to clear!",
                        color=discord.Color.gold()
                    ),
                    delete_after=10
                )

        required = self.required(ctx)
        player.clear_votes.add(ctx.author)

        if len(player.clear_votes) >= required:
            if player.is_playing:
                while player.is_playing:
                    await player.stop()

                return await ctx.send(
                    embed=discord.Embed(
                        description="Cleared the queue!",
                        color=discord.Color.green()
                    ),
                    delete_after=10
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        description="Nothing to clear!",
                        color=discord.Color.gold()
                    ),
                    delete_after=10
                )

            player.clear_votes.clear()
            return await player.stop()
        else:
            return await ctx.send(
                embed=discord.Embed(
                    description=f'{ctx.author.mention} has voted to clear the queue.',
                    color=discord.Color.dark_gold()
                ),
                delete_after=15
            )

    @commands.command(aliases=['swap'])
    async def swap_dj(self, ctx: commands.Context, *, member: discord.Member = None):
        """Swap the current DJ to another member in the voice channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            await ctx.send(
                embed=discord.Embed(
                    description='Only admins and the DJ may use this command.',
                    color=discord.Color.red()
                ),
                delete_after=15
            )
            return

        members = self.bot.get_channel(int(player.channel_id)).members

        if member and member not in members:
            await ctx.send(
                embed=discord.Embed(
                    description=f'{member} is not currently in voice, so can not be a DJ.',
                    color=discord.Color.red()
                ),
                delete_after=15
            )
            return

        if member and member == player.dj:
            await ctx.send(
                embed=discord.Embed(
                    description='Cannot swap DJ to the current DJ.',
                    color=discord.Color.red()
                ),
                delete_after=15
            )
            return

        if len(members) <= 2:
            await ctx.send(
                embed=discord.Embed(
                    description='No more members to swap to.',
                    color=discord.Color.red()
                ),
                delete_after=15
            )
            return

        if member:
            player.dj = member
            await ctx.send(
                embed=discord.Embed(
                    description=f'{member.mention} is now the DJ.',
                    color=discord.Color.green()
                ),
                delete_after=15
            )
            return

        for mem in members:
            if mem == player.dj or mem.bot:
                continue
            else:
                player.dj = mem
                await ctx.send(
                    embed=discord.Embed(
                        description=f'{member.mention} is now the DJ.',
                        color=discord.Color.green()
                    ),
                    delete_after=15
                )
                return


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
