import logging
from collections import defaultdict
from dataclasses import dataclass


logger = logging.getLogger(__name__)

@dataclass
class TunerData:
    user: dict
    user_top_artists: dict

    @property
    def artists(self) -> list[str]:
        artists = []
        for idx, item in enumerate(self.user_top_artists["items"]):
            artist = item["name"]
            artists.append(artist)
        return artists

    @property
    def genres(self) -> list[tuple[str, int]]:
        genres = defaultdict(lambda: 0)
        for idx, item in enumerate(self.user_top_artists["items"]):
            for genre in item["genres"]:
                genres[genre] += 1
        return sorted(list(genres.items()), key=lambda x: -x[1])


    @property
    def db_metadata(self):
        return {
            "display_name": self.user["display_name"],
            "url": self.user["external_urls"]["spotify"],
            "genres": [f"{count}:{genre}" for count, genre in self.genres],
            "artists": self.artists,
        }


def get_data(sp):
    logger.info("Fetching user data")
    return TunerData(
        sp.current_user(),
        sp.current_user_top_artists(),
    )


def match_overlap(match, data):
    genres = data.genres
    artists = data.artists
    # Display results
    match_artists = match["metadata"]["artists"]

    match_genres = {}
    for g in match["metadata"]["genres"]:
        genre, count = g.split(":", 1)
        match_genres[genre] = int(count)
    match_genres = sorted(list(match_genres.items()), key=lambda x: -x[1])

    shared_genres = set()
    for i in range(3):
        shared_genres.add(genres[i][0].strip().title())
        shared_genres.add(match_genres[i][0].strip().title())

    shared_artists = set(match_artists).intersection(set(artists))
    recommended_artists = [a for a in match_artists if a not in shared_artists]
    return shared_genres, shared_artists, recommended_artists
