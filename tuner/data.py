import logging
from collections import defaultdict


logger = logging.getLogger(__name__)

def get_data(sp):
    logger.info("Fetching user data")
    user = sp.current_user()
    results = sp.current_user_top_artists()

    # Collect genre counts
    logger.info("Counting genre appearances")
    genres = defaultdict(lambda: 0)
    logger.debug("Top artists:")
    artists = []
    for idx, item in enumerate(results["items"]):
        artist = item["name"]
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

    return user, artists, genres


def match_overlap(match, genres, artists):
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
