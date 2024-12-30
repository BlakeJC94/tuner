import json

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler

from tuner.globals import SCOPE

load_dotenv()

cache_handler = MemoryCacheHandler()
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=SCOPE,
        show_dialog=True,
        cache_handler=cache_handler,
    ),
)

# %% What is the schema we need?
# `get_data` needs current_user and current_user_top_artists

user = sp.current_user()
print(json.dumps(user, indent=2))
# {
#   "display_name": "consistencypls",
#   "external_urls": {
#     "spotify": "https://open.spotify.com/user/consistencypls"
#   },
#   "followers": {
#     "href": null,
#     "total": 3
#   },
#   "href": "https://api.spotify.com/v1/users/consistencypls",
#   "id": "consistencypls",
#   "images": [],
#   "type": "user",
#   "uri": "spotify:user:consistencypls"
# }

user_top_artists = sp.current_user_top_artists()
print(json.dumps(user_top_artists, indent=2))
# {
#   "items": [
#     {
#       "external_urls": {
#         "spotify": "https://open.spotify.com/artist/4pejUc4iciQfgdX6OKulQn"
#       },
#       "followers": {
#         "href": null,
#         "total": 3644720
#       },
#       "genres": [
#         "alternative metal",
#         "alternative rock",
#         "grunge",
#         "modern rock",
#         "palm desert scene",
#         "rock",
#         "stoner metal",
#         "stoner rock"
#       ],
#       "href": "https://api.spotify.com/v1/artists/4pejUc4iciQfgdX6OKulQn",
#       "id": "4pejUc4iciQfgdX6OKulQn",
#       "images": [
#         {
#           "height": 640,
#           "url": "https://i.scdn.co/image/ab6761610000e5eb909b2c4b7c768ee03445cd10",
#           "width": 640
#         },
#         {
#           "height": 320,
#           "url": "https://i.scdn.co/image/ab67616100005174909b2c4b7c768ee03445cd10",
#           "width": 320
#         },
#         {
#           "height": 160,
#           "url": "https://i.scdn.co/image/ab6761610000f178909b2c4b7c768ee03445cd10",
#           "width": 160
#         }
#       ],
#       "name": "Queens of the Stone Age",
#       "popularity": 71,
#       "type": "artist",
#       "uri": "spotify:artist:4pejUc4iciQfgdX6OKulQn"
#     },
#     {
#       "external_urls": {
#         "spotify": "https://open.spotify.com/artist/6wBUn8gMP85n8dPu6LoUcF"
#       },
#       "followers": {
#         "href": null,
#         "total": 84433
#       },
#       "genres": [
#         "double drumming",
#         "post-hardcore"
#       ],
#       "href": "https://api.spotify.com/v1/artists/6wBUn8gMP85n8dPu6LoUcF",
#       "id": "6wBUn8gMP85n8dPu6LoUcF",
#       "images": [
#         {
#           "height": 640,
#           "url": "https://i.scdn.co/image/ab6761610000e5eb7c5febf8798925a1b973a058",
#           "width": 640
#         },
#         {
#           "height": 320,
#           "url": "https://i.scdn.co/image/ab676161000051747c5febf8798925a1b973a058",
#           "width": 320
#         },
#         {
#           "height": 160,
#           "url": "https://i.scdn.co/image/ab6761610000f1787c5febf8798925a1b973a058",
#           "width": 160
#         }
#       ],
#       "name": "...And You Will Know Us by the Trail of Dead",
#       "popularity": 36,
#       "type": "artist",
#       "uri": "spotify:artist:6wBUn8gMP85n8dPu6LoUcF"
#     },
#   ],
#   "total": 204,
#   "limit": 20,
#   "offset": 0,
#   "href": "https://api.spotify.com/v1/me/top/artists?offset=0&limit=20&time_range=medium_term",
#   "next": "https://api.spotify.com/v1/me/top/artists?offset=20&limit=20&time_range=medium_term",
#   "previous": null
# }

# %% Get random usernames
import os
import requests

usernames_txt = "./scratch/data/usernames.txt"
if os.path.exists(usernames_txt):
    with open(usernames_txt, "r") as f:
        usernames = f.readlines()
else:
    response = requests.get(
        "https://usernameapiv1.vercel.app/API/random-usernames", params={"count": 128}
    )
    usernames = response.json()["usernames"]
    with open(usernames_txt, "w") as f:
        f.write("\n".join(usernames))

# %% Get all the playlists from spotify
# FUCK SPOTIFY PLAYLISTS ARE PRIVATE???
# from dataclasses import dataclass


# @dataclass
# class Playlist:
#     name: str
#     description: str
#     href: str

#     @classmethod
#     def from_item(cls, item):
#         return cls(
#             item["name"],
#             item["description"],
#             item["href"],
#         )

#     @classmethod
#     def from_row(cls, row):
#         return cls(*row.split(","))

#     def to_row(self):
#         return ",".join([self.name, self.description, self.href])


# playlists_txt = "./scratch/playlists.txt"
# if os.path.exists(playlists_txt):
#     with open(playlists_txt, "r") as f:
#         playlists = [Playlist.from_row(l) for l in f.readlines()]
# else:
#     all_playlists = []
#     raw_playlists = sp.user_playlists("spotify")
#     breakpoint()
#     while raw_playlists:
#         for i, item in enumerate(raw_playlists["items"]):
#             print(
#                 "%4d %s %s"
#                 % (i + 1 + raw_playlists["offset"], item["uri"], item["name"])
#             )
#             all_playlists.append(Playlist.from_item(item))
#         raw_playlists = sp.next(raw_playlists) if raw_playlists["next"] else None

#     top_playlists = [p for p in all_playlists if p.name.lower().startswith("top")]
#     the_playlists = [p for p in all_playlists if p.name.lower().startswith("the")]
#     num_playlists = [p for p in all_playlists if p.name.isnumeric()]

#     playlists = [
#         *top_playlists,
#         *the_playlists,
#         *num_playlists,
#     ]

#     with open(playlists_txt, "w") as f:
#         f.write(
#             "\n".join(
#                 [
#                     p.to_row()
#                     for p in playlists
#                 ]
#             )
#         )

# %% Manually search for popular public playlists from other users
playlist_ids = [
    "1xNWydoMmA8210KeHU948w",  # Chill electronic 2024
    "0MSCX9tZWQmitMQsfhvZIl",  # Indie playlist
    "6ZTpgxK6BT92mmsqwETj9l",  # Rap nation
    "09tdi9JkYgC7DP0XYBl4Az",  # Electronica and dance
    "19y0UVk0bcrJWEqMwBHosj",  # Liquidciuty Drum and Bass
    "0VPAV8Nq5HEoVP3z3Z3yvI",  # 2014 Tumblr
    "75shxelZjCWWDmNaH1iTKz",  # Hiphip and Rnb
    "2muZfMBGBB15kxI4V4dt4m",  # Rnb driving
    "3zf2ZaAhIhTBPAYSAiIGkd",  # Jazzhop lounge
    "5TkTomPbQuSNDxdlWg2fCx",  # BLues masters
    "56dbowk1V5ycS5jW7DSvi5",  # Blues rock
    "7lQu0IRGR1qTjWYdZbbKXE",  # County summer
    "5VusvMk3aK3O13G6K8JB7B",  # Latino vibes
    "6cVaEtcpf2BIhjtooyEHTp",  # Pop punk
    "31ymdYCITDnZRtkKzP3Itp",  # Pop top 50
    "3Ho3iO0iJykgEQNbjB2sic",  # Classic rock
    "1jLmAQunuUPZTACnENgzCx",  # Rock
    "5qNHuEyfs4QHR8NI4oNaxE",  # Rock
]


playlists_json = "./scratch/data/playlists.json"
if os.path.exists(playlists_json):
    with open(playlists_json, "r") as f:
        playlists = json.loads(f.read())
else:
    playlists = {}  # playlist_id -> artist_id -> artist_name
    for i, p in enumerate(playlist_ids):
        print(i + 1, "/", len(playlist_ids))
        try:
            results = sp.playlist_items(p)
        except:
            print(f"Couldn't load playlist {i} ({p})")
            continue
        foo = {
            a["id"]: a["name"]
            for item in results["items"]
            for a in item["track"]["artists"]
        }
        if len(foo) < 20:
            print(f"not enough artists in {p}")
            continue
        playlists[p] = foo
    with open(playlists_json, "w") as f:
        f.write(json.dumps(playlists, indent=2))


# %% Randomly sample 20 artists from playlists for each profile
import random

artists_txt = "./scratch/data/artists.txt"
if os.path.exists(artists_txt):
    with open(artists_txt, "r") as f:
        artists = f.readlines()
else:
    artists = []
    for i in range(len(usernames)):
        foo = list(random.choice(list(playlists.values())))
        selected_artists = random.sample(foo, 20)
        artists.append(",".join(selected_artists))
    with open(artists_txt, "w") as f:
        f.write("\n".join(artists))


# %% Create mock data for each row

def mock_data(username, user_artists):
    user = {
        "display_name": username,
        "external_urls": {"spotify": f"https://test.spotify.com/user/{username}"},
        "followers": {
            "href": None,
            "total": random.randint(0, 10),
        },
        "href": f"https://api.spotify.com/v1/users/{username}",
        "id": username,
        "images": [],
        "type": "user",
        "uri": f"mock:user:{username}",
    }

    user_top_artists = {
        "items": sp.artists(user_artists.strip().split(","))['artists'],
        "total": random.randint(22, 222),
        "limit": 20,
        "offset": 0,
        "href": "https://api.spotify.com/v1/foo/top/artists?offset=0&limit=20&time_range=medium_term",
        "next": "https://api.spotify.com/v1/foo/top/artists?offset=20&limit=20&time_range=medium_term",
        "previous": None,
    }

    return {
        "user": user,
        "user_top_artists": user_top_artists,
    }


users_json = "./scratch/data/users.json"
if os.path.exists(users_json):
    with open(users_json, "r") as f:
        users =json.loads(f.read())
else:
    users = []
    for i, (username, user_artists) in enumerate(zip(usernames, artists)):
        print(i + 1, "/", len(usernames))
        users.append(mock_data(username, user_artists))
    with open(users_json, "w") as f:
        f.write(json.dumps(users, indent=2))

# %% Load into database
from tuner.core import (
    get_genre_vec,
    get_pinecone_index,
    TunerMetadata,
    upload_genre_vector,
)
from tuner.data import TunerData

for i, user in enumerate(users):
    print(i + 1, "/", len(users))

    user_data = TunerData(
        user['user'],
        user['user_top_artists'],
    )

    # Get genre embeddings
    genre_vec = get_genre_vec(user_data)

    # Log to database
    index = get_pinecone_index()
    user_metadata = TunerMetadata.from_data(user_data)
    upload_genre_vector(index, user_metadata, genre_vec)
