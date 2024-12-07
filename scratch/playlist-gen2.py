import os
import random

from dotenv import load_dotenv
import pylast
import spotipy
import requests

from tuner.globals import SCOPE


BASE_URL = "https://api.deezer.com"

load_dotenv()

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

artists = [
    ("2d0hyoQ5ynDBnkvAbJKORj", "rage against the machine"),
    ("3ExT45ORJ8pT516HRZbr7G", "the living end"),
    ("7MhMgCo0Bl0Kukl93PZbYS", "blur"),
]


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

        # Select top 3 songs
        top_tracks = get_top_tracks(sp, artist_id)
        top_tracks = random.sample(top_tracks, 3)

        # Get 3 related songs for each song on lastfm
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
        breakpoint()
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
