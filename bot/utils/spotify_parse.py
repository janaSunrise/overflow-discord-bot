import typing as t

import discord
import spotify
import wavelink
from discord.ext import commands


class SpotifyTrack:
    def __init__(self, track: spotify.Track, requester):
        self.title = track.name
        self.artists = ', '.join(artist.name for artist in track.artists)
        self.description = f"{self.title} - {self.artists}"
        self.url = track.url
        self.requester = requester


async def get_spotify_tracks(
        ctx, search_type: str, spotify_id: str, spotify_client, spotify_http
) -> t.Tuple[str, list]:
    name = None
    search_tracks = None

    try:
        if search_type == 'album':
            search_result = await spotify_client.get_album(spotify_id=spotify_id)

            name = search_result.name
            search_tracks = await search_result.get_all_tracks()

            if len(search_tracks) > 500:
                search_tracks = search_tracks[:500]

        elif search_type == 'playlist':
            search_result = spotify.Playlist(
                client=spotify_client,
                data=await spotify_http.get_playlist(spotify_id)
            )
            name = search_result.name
            search_tracks = list(await search_result.get_all_tracks())

            if len(search_tracks) > 500:
                search_tracks = search_tracks[:500]

        elif search_type == 'track':
            search_result = await spotify_client.get_track(spotify_id=spotify_id)
            name = search_result.name
            search_tracks = [search_result]

    except spotify.NotFound or discord.HTTPException:
        return await ctx.send(f'No results were found for your spotify link.', delete_after=15)

    return name, search_tracks


async def play_tracks(ctx: commands.Context, player: wavelink.Player, tracks: list, requester):
    for track in tracks:
        if not track:
            continue
        await player.queue.put(SpotifyTrack(track, requester))

    if not player.is_playing:
        await player.do_next()


async def play(
        ctx: commands.Context, player: wavelink.Player, search_type: str, spotify_id: str, spotify_client, spotify_http
):
    requester = ctx.author
    name, tracks = await get_spotify_tracks(ctx, search_type, spotify_id, spotify_client, spotify_http)

    await play_tracks(ctx, player, tracks, requester)

    if not name:
        return await ctx.send(
            embed=discord.Embed(
                description=f'```ini\nAdded {tracks[0].title} to the Queue\n```',
                color=discord.Color.blurple()
            ),
            delete_after=10
        )

    await ctx.send(
        embed=discord.Embed(
            description=f"```ini\nAdded the playlist {name} with {len(tracks)} songs to the queue.\n```",
            color=discord.Color.blurple()
        ),
        delete_after=10
    )


