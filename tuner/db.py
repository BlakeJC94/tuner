import os

from pinecone.grpc import PineconeGRPC as Pinecone

from tuner.globals import PINECONE_HOST


def get_pinecone_index():
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    return pc.Index(host=PINECONE_HOST)


def upload_genre_vector(index, data, genre_vec):
    index.upsert(
        vectors=[
            {
                "id": data.user["uri"],
                "values": genre_vec,
                "metadata": data.db_metadata,
            },
        ]
    )


def search_for_matches(index, data, genre_vec):
    user = data.user
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
