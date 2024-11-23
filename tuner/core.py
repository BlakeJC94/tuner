import logging

from tuner.encode import get_genre_vec
from tuner.db import (
    TunerMetadata,
    get_pinecone_index,
    upload_genre_vector,
    search_for_matches,
    select_match,
)
from tuner.data import get_data
from tuner.utils import get_spotify_client

logger = logging.getLogger(__name__)


def tuner_match(session=None):
    logger.info("Logging into Spotify")
    sp = get_spotify_client(session)

    # Get data
    user_data = get_data(sp)

    # Get genre embeddings
    logger.info("Embedding genres")
    genre_vec = get_genre_vec(user_data)

    # Log to database
    logger.info("Logging to database")
    index = get_pinecone_index()
    user_metadata = TunerMetadata.from_data(user_data)
    upload_genre_vector(index, user_metadata, genre_vec)

    # Get other users
    logger.info("Searching for matches")
    matches = search_for_matches(index, user_metadata, genre_vec)

    if not matches:
        logger.warning("No matches found")
        return None, [], [], []

    logger.info("Printing result")
    score, match_metadata = select_match(matches)
    shared_genres, shared_artists, recommended_artists = match_metadata.overlap(
        user_metadata
    )

    return match_metadata, shared_genres, shared_artists, recommended_artists
