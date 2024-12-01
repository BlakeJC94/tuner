import os

from dotenv import load_dotenv
import pylast

load_dotenv()
# %%

lfm = pylast.LastFMNetwork(
    api_key=os.environ["LASTFM_API_KEY"],
    api_secret=os.environ["LASTFM_API_SECRET"],
)

# %%
def get_similar_artists(artist_name, limit=5):
    artist = lfm.get_artist(artist_name)
    similar_artists = artist.get_similar(limit=limit)
    return [artist.item.name for artist in similar_artists]

artists = ["Rage Against The Machine", "Pink Floyd"]
for a in artists:
    print(a)
    for b in get_similar_artists(a):
        print("  ", b)

# %%
def get_top_tracks(artist_name, limit=3):
    artist = lfm.get_artist(artist_name)
    top_tracks = artist.get_top_tracks(limit=limit)
    breakpoint()
    return [t.item.title for t in top_tracks]

artists = ["Rage Against The Machine", "Pink Floyd"]
for a in artists:
    print(a)
    for b in get_similar_artists(a):
        print("  ", b)
        for c in get_top_tracks(b):
            print("    ", c)
