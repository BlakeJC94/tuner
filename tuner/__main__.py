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
    user = sp.current_user()
    results = sp.current_user_top_artists()

    # Collect genre counts
    genres = defaultdict(lambda: 0)
    print("\n", "Top artists:")
    for idx, item in enumerate(results["items"]):
        print(f"{idx:02} - {item['name']}")
        for genre in item["genres"]:
            genres[genre] += 1

    genres = sorted(list(genres.items()), key=lambda x: -x[1])

    print("\n", "Genre counts:")
    for genre, count in genres:
        if count < 2:
            continue
        print(count, genre)

    # Get genre embeddings
    embeddings = {g: model.encode(g).reshape(1, -1) for g, _ in genres}

    # Create genre vector
    genre_vec = get_genre_vec(genres, embeddings)

    # TODO Log to database
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(
        host="https://tuner-genre-vecs-all-minilm-l6-v2-w50ynqp.svc.aped-4627-b74a.pinecone.io"
    )
    index.upsert(
        vectors=[
            {
                "id": user["uri"],
                "values": genre_vec[0].tolist(),
                "metadata": {
                    "display_name": user["display_name"],
                    "url": user["external_urls"]["spotify"],
                    "genres": [f"{count}:{genre}" for count, genre in genres],
                },
            },
        ]
    )

    print("Done!")


if __name__ == "__main__":
    main()
