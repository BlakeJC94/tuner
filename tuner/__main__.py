import os
from collections import defaultdict

import spotipy
import numpy as np
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
from sentence_transformers import SentenceTransformer
from pinecone.grpc import PineconeGRPC as Pinecone

load_dotenv()

SCOPE = [
    "user-top-read",
    # "user-read-recently-played",  # Is there a way to use this?
]

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_genre_vec(
    genre_counts: list[tuple[str, int]],
    embeddings: dict[str, np.ndarray],
) -> np.ndarray:
    weighted_embeddings = np.zeros_like(list(embeddings.values())[0])
    for genre, count in genre_counts:
        weighted_embeddings += embeddings[genre] * count
    return weighted_embeddings / np.linalg.norm(weighted_embeddings)


def main():
    """Main entrypoint for Tuner."""

    # Log into Spotify
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=SCOPE,
            show_dialog=True,
            # cache_handler=MemoryCacheHandler(),  # TODO upgrade to flask cache
        ),
    )

    # Get data
    user = sp.current_user()
    results = sp.current_user_top_artists()

    # Collect genre counts
    genres = defaultdict(lambda: 0)
    # print("\n", "Top artists:")
    for idx, item in enumerate(results["items"]):
        # print(f"{idx:02} - {item['name']}")
        for genre in item["genres"]:
            genres[genre] += 1

    genres = sorted(list(genres.items()), key=lambda x: -x[1])

    # print("\n", "Genre counts:")
    # for genre, count in genres:
    #     if count < 2:
    #         continue
    #     print(count, genre)

    # Get genre embeddings
    embeddings = {g: model.encode(g).reshape(1, -1) for g, _ in genres}

    # Create genre vector
    genre_vec = get_genre_vec(genres, embeddings)
    genre_vec = genre_vec[0].tolist()

    # TODO Log to database
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(
        host="https://tuner-genre-vecs-all-minilm-l6-v2-w50ynqp.svc.aped-4627-b74a.pinecone.io"
    )
    index.upsert(
        vectors=[
            {
                "id": user["uri"],
                "values": genre_vec,
                "metadata": {
                    "display_name": user["display_name"],
                    "url": user["external_urls"]["spotify"],
                    "genres": [f"{count}:{genre}" for count, genre in genres],
                },
            },
        ]
    )

    # Get other users
    matches = index.query(
        vector=genre_vec,
        top_k=4,
        include_values=False,
        include_metadata=True,
    ).to_dict().get('matches', [])
    matches = sorted((m for m in matches if m['id'] != user['uri']), key=lambda x: -x['score'])

    if not matches:
        print("No matches found, check back later when more users use Tuner.")
        return 0

    match = matches[0]

    # Display results
    match_display_name = match['metadata']["display_name"]
    match_url = match['metadata']["url"]

    match_genres = {}
    for g in match['metadata']["genres"]:
        genre, count = g.split(":", 1)
        match_genres[genre] = int(count)
    match_genres = sorted(list(match_genres.items()), key=lambda x: -x[1])

    shared_genres = set()
    for i in range(3):
        shared_genres.add(genres[i][0].strip().title())
        shared_genres.add(match_genres[i][0].strip().title())

    print(f"Match found: '{match_display_name}'", "\n")
    print("You have a shared interest in the following genres:")
    for g in shared_genres:
        print(f"- {g}")
    print("")
    print(f"Check out their profile at {match_url}")

    print("Done!")
    return 0


if __name__ == "__main__":
    main()
