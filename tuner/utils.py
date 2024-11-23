import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler, FlaskSessionCacheHandler

from tuner.globals import SCOPE


def get_spotify_client(session=None):
    load_dotenv()
    cache_handler = (
        FlaskSessionCacheHandler(session)
        if session is not None
        else MemoryCacheHandler()
    )
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=SCOPE,
            show_dialog=True,
            # cache_handler=cache_handler,
        ),
    )


def display_match(match, shared_genres, shared_artists, recommended_artists):
    if not match:
        print("No matches found, check back later when more users use Tuner.")

    match_display_name = match.display_name
    match_url = match.url

    print(f"Match found: '{match_display_name}'")
    print("")
    print("You have a shared interest in the following genres:")
    for g in shared_genres:
        print(f"- {g}")
    print("")

    if shared_artists:
        print("You both enjoy the following artists:")
        for a in list(shared_artists)[:3]:
            print(f"- {a}")
        print("")

    print(f"'{match_display_name}' also enjoys the following artists:")
    for a in recommended_artists[:6]:
        print(f"- {a}")
    print("")

    print("Check out their public playlists on their Spotify profile:")
    print(f"    {match_url}")
