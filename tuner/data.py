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


def get_data(sp):
    logger.info("Fetching user data")
    return TunerData(
        sp.current_user(),
        sp.current_user_top_artists(),
    )
