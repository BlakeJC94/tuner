import os
import random
import asyncio
import time
from dataclasses import dataclass
from datetime import timedelta

import aiohttp
import pylast
import spotipy
from dotenv import load_dotenv

from tuner.globals import SCOPE


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
async def fetch_json(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict | None = None,
    params: dict | None = None,
) -> dict:
    params = params or {}
    headers = headers or {}
    async with session.get(url, headers=headers, params=params) as response:
        response.raise_for_status()
        return await response.json()


# %%
async def get_top_tracks(
    session: aiohttp.ClientSession,
    access_token: str,
    artist_id: str,
) -> list[Track]:
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    data = await fetch_json(
        session, url, headers={"Authorization": f"Bearer {access_token}"}
    )
    return [Track.from_spotify_track(t) for t in data["tracks"]]

    # def fetch_tracks():
    #     output = []
    #     tracks = sp.artist_top_tracks(artist_id)["tracks"]  # FIXME
    #     for track in tracks:
    #         output.append(Track.from_spotify_track(track))
    #     return output
    # return await asyncio.to_thread(fetch_tracks)


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

    return await asyncio.to_thread(fetch_similar_tracks, lfm, track)


# %%
async def get_spotify_match(
    session: aiohttp.ClientSession,
    access_token: str,
    track: Track,
) -> Track | None:
    url = "https://api.spotify.com/v1/search"
    data = await fetch_json(
        session,
        url,
        params={
            "q": f"track:{track.name} artist:{track.artists}",
            "type": "track",
            "limit": 1,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not data["tracks"]["items"]:
        return None
    return Track.from_spotify_track(data["tracks"]["items"][0])


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

    return await asyncio.to_thread(fetch_similar_artists, lfm, artist)


# %%
async def get_top_tracks_lfm(lfm: pylast.LastFMNetwork, artist: Artist) -> list[Track]:
    def fetch_top_tracks_lfm(lfm, artist):
        return [
            Track.from_lfm(t.item) for t in artist.lfm_result.get_top_tracks(limit=10)
        ]

    return await asyncio.to_thread(fetch_top_tracks_lfm, lfm, artist)


# %%
class RateLimiter:
    def __init__(self, rate_limit, period):
        self.rate_limit = rate_limit
        self.period = period
        self.semaphore = asyncio.Semaphore(rate_limit)
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            await self.semaphore.acquire()
        asyncio.create_task(self.release())

    async def release(self):
        await asyncio.sleep(self.period)
        self.semaphore.release()


async def add_preview_url(
    session: aiohttp.ClientSession,
    access_token: str,
    track: Track,
    rate_limiter: RateLimiter,
) -> Track:
    url = f"{BASE_URL}/search"
    await rate_limiter.acquire()
    data = await fetch_json(
        session,
        url,
        params={"q": f'track:"{track.name}" artist:"{track.artists}"'},
    )
    if "data" not in data or not data["data"]:
        print("BLOOF")
        return track
    track.preview_url = data["data"][0].get("preview")


# %%
# TODO RFC to put similar artists at the top
async def process_artist(
    session: aiohttp.ClientSession,
    access_token: str,
    lfm: pylast.LastFMNetwork,
    artist: Artist,
) -> list[Track]:
    print(artist.name)
    tracks = []

    # Get random 3 tracks
    top_tracks = await get_top_tracks(session, access_token, artist.id)
    top_tracks = random.sample(top_tracks, 3)
    tracks.extend(top_tracks)

    for track in top_tracks:
        # Get similar track for each top track
        similar_tracks = await get_similar_tracks(lfm, track)
        # Match each track to Spotify
        spotify_matches = await asyncio.gather(
            *[
                get_spotify_match(session, access_token, track)
                for track in similar_tracks
            ]
        )
        tracks.extend(spotify_matches)

    # Get similar artists and top 5 tracks for each
    similar_artists = await get_similar_artists(lfm, artist)

    # Get top 5 tracks for each similar artist
    for similar_artist in similar_artists:
        similar_artist_top_tracks = await get_top_tracks_lfm(lfm, similar_artist)
        spotify_matches = await asyncio.gather(
            *[
                get_spotify_match(session, access_token, track)
                for track in random.sample(similar_artist_top_tracks, 3)
            ]
        )
        tracks.extend(spotify_matches)

    # Filter no matches and get audio sample for each
    rate_limiter = RateLimiter(rate_limit=3, period=1)
    tracks = await asyncio.gather(
        *[add_preview_url(session, access_token, track, rate_limiter) for track in tracks if track is not None]
    )

    return tracks


# %%
async def main(
    access_token: str, artists: list[tuple[str, str]]
) -> list[dict[str, str]]:
    lfm = pylast.LastFMNetwork(
        api_key=os.environ["LASTFM_API_KEY"],
        api_secret=os.environ["LASTFM_API_SECRET"],
    )

    async with aiohttp.ClientSession() as session:
        tasks = [
            process_artist(session, access_token, lfm, artist) for artist in artists
        ]
        results = await asyncio.gather(*tasks)

    return results


artists = [
    Artist(id="2d0hyoQ5ynDBnkvAbJKORj", name="rage against the machine"),
    Artist(id="3ExT45ORJ8pT516HRZbr7G", name="the living end"),
    Artist(id="7MhMgCo0Bl0Kukl93PZbYS", name="blur"),
]
cache_handler = spotipy.cache_handler.CacheFileHandler()
auth_manager = spotipy.oauth2.SpotifyOAuth(
    scope=SCOPE,
    cache_handler=cache_handler,
    show_dialog=True,
)
access_token = auth_manager.get_cached_token()["access_token"]

start = time.time()
foo = asyncio.run(main(access_token, artists))
dt = time.time() - start
print(f"Time taken: {timedelta(seconds=dt)}")
