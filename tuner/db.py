import os

from pinecone.grpc import PineconeGRPC as Pinecone

from tuner.globals import PINECONE_HOST


def get_pinecone_index():
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    return pc.Index(host=PINECONE_HOST)


def upload_genre_vector(index, user, genre_vec, genres, artists):
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


def search_for_matches(index, user, genre_vec):
    matches = (
        index.query(
            vector=genre_vec,
            top_k=4,
            include_values=False,
            include_metadata=True,
        )
        .to_dict()
        .get("matches", [])
    )
    return sorted(
        (m for m in matches if m["id"] != user["uri"]), key=lambda x: -x["score"]
    )


def select_match(matches):  # TODO Random selection
    return matches[0]
