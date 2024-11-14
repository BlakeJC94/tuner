import logging
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

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


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
    model = SentenceTransformer("all-MiniLM-L6-v2")

    logger.info("Logging into Spotify")
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=SCOPE,
            show_dialog=True,
            # cache_handler=MemoryCacheHandler(),  # TODO upgrade to flask cache
        ),
    )

    # Get data
    logger.info("Fetching user data")
    user = sp.current_user()
    results = sp.current_user_top_artists()

    # Collect genre counts
    logger.info("Counting genre appearances")
    genres = defaultdict(lambda: 0)
    logger.debug("Top artists:")
    artists = []
    for idx, item in enumerate(results["items"]):
        artist = item['name']
        artists.append(artist)
        logger.debug(f"{idx:02} - {artist}")
        for genre in item["genres"]:
            genres[genre] += 1

    genres = sorted(list(genres.items()), key=lambda x: -x[1])

    logger.debug("Genre counts:")
    for genre, count in genres:
        if count < 2:
            continue
        logger.debug(count, genre)

    # Get genre embeddings
    logger.info("Embedding genres")
    embeddings = {g: model.encode(g).reshape(1, -1) for g, _ in genres}
    genre_vec = get_genre_vec(genres, embeddings)
    genre_vec = genre_vec[0].tolist()

    # Log to database
    logger.info("Logging to database")
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
                    "artists": artists,
                },
            },
        ]
    )

    # Get other users
    logger.info("Searching for matches")
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

    logger.info("Printing result")
    match = matches[0]

    # Display results
    match_display_name = match['metadata']["display_name"]
    match_url = match['metadata']["url"]
    match_artists = match['metadata']["artists"]

    match_genres = {}
    for g in match['metadata']["genres"]:
        genre, count = g.split(":", 1)
        match_genres[genre] = int(count)
    match_genres = sorted(list(match_genres.items()), key=lambda x: -x[1])

    shared_genres = set()
    for i in range(3):
        shared_genres.add(genres[i][0].strip().title())
        shared_genres.add(match_genres[i][0].strip().title())

    shared_artists = set(match_artists).intersection(set(artists))
    recommended_artists = [a for a in match_artists if a not in shared_artists]

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


    logging.info("Done!")
    return 0


if __name__ == "__main__":
    main()
