import logging

from tuner.encode import get_genre_vec
from tuner.db import (
    get_pinecone_index,
    upload_genre_vector,
    search_for_matches,
    select_match,
)
from tuner.data import get_data, match_overlap
from tuner.utils import get_spotify_client

logger = logging.getLogger(__name__)


def tuner_match(session=None):
    logger.info("Logging into Spotify")
    sp = get_spotify_client(session)

    # Get data
    data = get_data(sp)

    # Get genre embeddings
    logger.info("Embedding genres")
    genre_vec = get_genre_vec(data)

    # Log to database
    logger.info("Logging to database")
    index = get_pinecone_index()
    upload_genre_vector(index, data, genre_vec)

    # Get other users
    logger.info("Searching for matches")
    matches = search_for_matches(index, data, genre_vec)

    if not matches:
        logger.warning("No matches found")
        return None, [], [], []

    logger.info("Printing result")
    match = select_match(matches)
    shared_genres, shared_artists, recommended_artists = match_overlap(
        match,
        data,
    )
    return match, shared_genres, shared_artists, recommended_artists
