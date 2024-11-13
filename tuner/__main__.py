from collections import defaultdict

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler

load_dotenv()

SCOPE = [
    "user-top-read",
    # "user-read-recently-played",  # Is there a way to use this?
]


def main():
    print("Hello from tuner!")
    # Log into Spotify
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=SCOPE,
            show_dialog=True,
            cache_handler=MemoryCacheHandler(),  # TODO upgrade to flask cache
        ),
    )

    # Get data
    results = sp.current_user_top_artists()

    # Collect genre counts
    genres = defaultdict(lambda: 0)
    print("\n", "Top artists:")
    for idx, item in enumerate(results['items']):
        print(f"{idx:02} - {item['name']}")
        for genre in item['genres']:
            genres[genre] += 1

    print("\n", "Genre counts:")
    for genre, count in sorted(list(genres.items()), key=lambda x: -x[1]):
        if count < 2:
            continue
        print(count, genre)

    # TODO Get genre embeddings
    # TODO Create genre vector
    # TODO Log to database


if __name__ == "__main__":
    main()
