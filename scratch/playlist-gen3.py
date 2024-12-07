import os
import random

from dotenv import load_dotenv
import pylast
import spotipy
import requests

from tuner.globals import SCOPE


# %%
def get_top_tracks(sp, artist_id: str) -> list[dict[str]]:
    output = []
    tracks = sp.artist_top_tracks(artist_id)["tracks"]
    for track in tracks:
        output.append(
            {
                "name": track["name"],
                "album": track["album"]["name"],
                "artists": ", ".join([a["name"] for a in track["artists"]]),
                "image_url": next(
                    (i["url"] for i in track["album"]["images"] if i["height"] == 64),
                    None,
                ),
                "uri": track["uri"],
                "preview_url": None,
            }
        )
    return output


foo, bar = artists[0]
baz = get_top_tracks(sp, foo)
print(baz)

# %%
# %%
# %%
# %%


def get_playlist(artists: list[tuple[str, str]]) -> list[dict[str, str]]:
    playlist_tracks = []
    # For each artist
    for artist_id, artist_name in artists:
        print(artist_name)
        related_tracks = []  # lfm

        # Select top 3 songs and Get 3 related songs for each song on lastfm
        for track in random.sample(sp.artist_top_tracks(artist_id)["tracks"], 3):
            try:
                lfm_track = lfm.get_track(artist_name, track["name"])
            except Exception:
                continue
            similar_tracks = [i.item for i in lfm_track.get_similar(limit=3)]
            related_tracks.extend(similar_tracks)

        # Select 4 related artists on lastfm
        try:
            artist = lfm.get_artist(artist_name)
            related_artists = artist.get_similar(limit=4)
        except Exception:
            related_artists = []
        related_artists = [r.item for r in related_artists]

        # Get 6 of their top songs on lastfm
        for related_artist in related_artists:
            related_top_tracks = [
                t.item for t in related_artist.get_top_tracks(limit=10)
            ]
            related_top_tracks = random.sample(related_top_tracks, 6)
            related_tracks.extend(related_top_tracks)

        # Get spotify ID for each song
        for track in related_tracks:
            track_name = track.title
            artist = track.artist.name
            results = sp.search(
                f"track:{track_name} artist:{artist}", type="track", limit=1
            )["tracks"]["items"]
            if not results:
                continue
            result = results[0]
            playlist_tracks.append(
                {
                    "name": result["name"],
                    "album": result["album"]["name"],
                    "artists": ", ".join([a["name"] for a in result["artists"]]),
                    "image_url": next(
                        (
                            i["url"]
                            for i in result["album"]["images"]
                            if i["height"] == 64
                        ),
                        None,
                    ),
                    "uri": result["uri"],
                    "preview_url": None,
                }
            )

    # Shuffle list and select 12
    playlist_tracks = random.sample(playlist_tracks, 12)

    # Get audio sample for each
    for track in playlist_tracks:
        track_name, artist_name = track["name"], track["artists"]
        query = f'track:"{track_name}" artist:"{artist_name}"'
        response = requests.get(f"{BASE_URL}/search", params={"q": query})
        if not response.ok:
            continue
        data = response.json()
        if not data["data"]:
            continue
        track["preview_url"] = data["data"][0].get("preview")

    return playlist_tracks


foo = get_playlist(artists)


################################
# %% Asyncio and threading this mofo
import asyncio
import aiohttp
from typing import Any
from dataclasses import dataclass

BASE_URL = "https://api.deezer.com"

load_dotenv()


@dataclass
class Track:
    name: str
    artists: str
    uri: str | None = None
    album: str | None = None
    image_url: str | None = None
    preview_url: str | None = None

    @classmethod
    def from_spotify_track(cls, track: dict[str, str]):
        return cls(
            name=track["name"],
            album=track["album"]["name"],
            artists=", ".join([a["name"] for a in track["artists"]]),
            image_url=next(
                (i["url"] for i in track["album"]["images"] if i["height"] == 64),
                None,
            ),
            uri=track["uri"],
            preview_url=None,
        )

    @classmethod
    def from_lfm(cls, track):
        return cls(
            name=track.title,
            artists=track.artist.name,
        )


@dataclass
class Artist:  # TODO lfm type
    name: str
    id: str | None = None
    lfm_result: pylast.Artist | None = None

    @classmethod
    def from_lfm(cls, result: pylast.Artist):
        return cls(name=result.name, lfm_result=result)


# %%
# TODO consider aiospotify.py lib if things don't work
async def get_top_tracks(sp: spotipy.Spotify, artist_id: str) -> list[Track]:
    def fetch_tracks():
        output = []
        tracks = sp.artist_top_tracks(artist_id)["tracks"]
        for track in tracks:
            output.append(Track.from_spotify_track(track))
        return random.sample(output, 3)

    return await asyncio.to_thread(fetch_tracks)


# %%
async def get_similar_tracks(
    lfm: pylast.LastFMNetwork,
    track: Track,
) -> list[Track]:
    def fetch_similar_tracks(lfm, track):
        try:
            lfm_track = lfm.get_track(track.artists, track.name)
        except Exception:
            return []
        similar_tracks = [
            Track(
                name=i.item.title,
                artists=i.item.artist.name,
            )
            for i in lfm_track.get_similar(limit=3)
        ]
        return similar_tracks

    return await asyncio.to_thread(fetch_similar_tracks(lfm, track))


# %%
async def get_spotify_match(sp: spotipy.Spotify, track: Track) -> Track:
    def fetch_spotify_match(sp, track):
        results = sp.search(
            f"track:{track.name} artist:{track.artists}", type="track", limit=1
        )["tracks"]["items"]
        if not results:
            return None
        result = results[0]
        return Track.from_spotify_track(result)

    return await asyncio.to_thread(fetch_spotify_match(sp, track))


# %%
async def get_similar_artists(
    lfm: pylast.LastFMNetwork,
    artist: Artist,
) -> list[Artist]:
    def fetch_similar_artists(lfm, artist):
        try:
            artist = lfm.get_artist(artist.name)
            related_artists = artist.get_similar(limit=4)
        except Exception:
            return []
        return [Artist.from_lfm(r.item) for r in related_artists]

    return await asyncio.to_thread(fetch_similar_artists(lfm, artist))


# %%
async def get_top_tracks_lfm(lfm: pylast.LastFMNetwork, artist: Artist) -> list[Track]:
    def fetch_top_tracks_lfm(lfm, artist):
        return [
            Track.from_lfm(t.item) for t in artist.lfm_result.get_top_tracks(limit=10)
        ]

    return await asyncio.to_thread(fetch_top_tracks_lfm(lfm, artist))


# %%
# TODO RFC to put similar artists at the top
async def process_artist(
    session: aiohttp.ClientSession,
    sp: spotipy.Spotify,
    lfm: pylast.LastFMNetwork,
    artist: Artist,
) -> list[Track]:
    result = dict(artist=artist.name, tracks=[])  # TODO check return type

    # Get random 3 tracks
    top_tracks = await get_top_tracks(sp, artist.id)
    top_tracks = random.sample(top_tracks, 3)
    result["tracks"].extend(top_tracks)

    for track in top_tracks:
        # Get similar track for each top track
        similar_tracks = await get_similar_tracks(lfm, track)
        # Match each track to Spotify
        spotify_matches = await asyncio.gather(
            *[get_spotify_match(sp, track) for track in similar_tracks]
        )
        result["tracks"].extend(spotify_matches)

    # Get similar artists and top 5 tracks for each
    similar_artists = await get_similar_artists(lfm, artist)

    # Get top 5 tracks for each similar artist
    for similar_artist in similar_artists:
        similar_artist_top_tracks = await get_top_tracks_lfm(lfm, similar_artist)
        spotify_matches = await asyncio.gather(
            *[
                get_spotify_match(sp, track)
                for track in random.sample(similar_artist_top_tracks, 3)
            ]
        )
        result["tracks"].extend(spotify_matches)

    return result


# %%
async def main(artists: list[tuple[str, str]]) -> list[dict[str, str]]:
    cache_handler = spotipy.cache_handler.MemoryCacheHandler()
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope=SCOPE,
        cache_handler=cache_handler,
        show_dialog=True,
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)

    lfm = pylast.LastFMNetwork(
        api_key=os.environ["LASTFM_API_KEY"],
        api_secret=os.environ["LASTFM_API_SECRET"],
    )

    async with aiohttp.ClientSession() as session:
        tasks = [process_artist(session, sp, lfm, artist) for artist in artists]
        results = await asyncio.gather(*tasks)

    return results


artists = [
    Artist(id="2d0hyoQ5ynDBnkvAbJKORj", name="rage against the machine"),
    Artist(id="3ExT45ORJ8pT516HRZbr7G", name="the living end"),
    Artist(id="7MhMgCo0Bl0Kukl93PZbYS", name="blur"),
]
foo = asyncio.run(main(artists))
# %%
