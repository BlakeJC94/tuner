import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler, FlaskSessionCacheHandler

from tuner.globals import SCOPE, GENRES_PATH


# TODO restore cache
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


def get_all_genres():
    with open(GENRES_PATH, "r") as f:
        genres = [g.strip().lower() for g in f.read().split("\n")]
    return genres


def display_match(output):
    if not output:
        print("No matches found, check back later when more users use Tuner.")

    match_display_name = output.match_md.display_name
    match_url = output.match_md.url

    print(f"Match found: '{match_display_name}'")
    print("")
    print("You have a shared interest in the following genres:")
    for g in output.shared_genres:
        print(f"- {g}")
    print("")

    if output.shared_artists:
        print("You both enjoy the following artists:")
        for a in output.shared_artists[:3]:
            print(f"- {a}")
        print("")

    print(f"'{match_display_name}' also enjoys the following artists:")
    for a in output.recommended_artists[:6]:
        print(f"- {a}")
    print("")

    print("Check out their public playlists on their Spotify profile:")
    print(f"    {match_url}")
