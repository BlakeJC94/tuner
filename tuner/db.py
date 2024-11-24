import os
from dataclasses import dataclass, asdict

from pinecone.grpc import PineconeGRPC as Pinecone

from tuner.globals import PINECONE_HOST


# TODO fix ID after updating db
@dataclass
class TunerMetadata:
    display_name: str
    url: str
    genres: list[str]
    artists: list[str]
    id: str = "foo"

    @classmethod
    def from_data(cls, data):
        return cls(
            id=data.user["uri"],
            display_name=data.user["display_name"],
            url=data.user["external_urls"]["spotify"],
            genres=[f"{count}:{genre}" for count, genre in data.genres],
            artists=data.artists,
        )

    @property
    def genre_counts(self) -> dict[str, int]:
        match_genres = {}
        for g in self.genres:
            genre, count = g.split(":", 1)
            genre = genre.strip().title()
            match_genres[genre] = int(count)
        return match_genres


@dataclass
class TunerOutput:
    match_md: TunerMetadata
    user_md: TunerMetadata

    @property
    def shared_genres(self) -> list[str]:
        genre_counts = self.match_md.genre_counts
        genre_counts_total = sum(genre_counts.values())

        other_genre_counts = self.user_md.genre_counts
        other_genre_counts_total = sum(other_genre_counts.values())

        common_genres = set(genre_counts.keys()).intersection(other_genre_counts.keys())
        shared_scores_genres = []
        for g in common_genres:
            score = (
                (genre_counts[g] / genre_counts_total)
                + (other_genre_counts[g] / other_genre_counts_total)
            ) / 2
            shared_scores_genres.append((score, g))

        shared_scores_genres = sorted(shared_scores_genres, key=lambda x: -x[0])
        return [g for _, g in shared_scores_genres]

    @property
    def shared_artists(self) -> list[str]:
        return list(set(self.match_md.artists).intersection(set(self.user_md.artists)))

    @property
    def recommended_artists(self) -> list[str]:
        return [a for a in self.match_md.artists if a not in self.shared_artists]


def get_pinecone_index():
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    return pc.Index(host=PINECONE_HOST)


def upload_genre_vector(index, db_metadata, genre_vec):
    index.upsert(
        vectors=[
            {
                "id": db_metadata.id,
                "values": genre_vec,
                "metadata": asdict(db_metadata),
            },
        ]
    )


def search_for_matches(
    index, db_metadata, genre_vec
) -> list[tuple[float, TunerMetadata]]:
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
    matches = [
        (m["score"], TunerMetadata(**m["metadata"]))
        for m in matches
        if m["id"] != db_metadata.id
    ]
    return sorted(matches, key=lambda x: -x[0])


# TODO Random selection
def select_match(
    matches: list[tuple[float, TunerMetadata]],
) -> tuple[float, TunerMetadata]:
    return matches[0]
