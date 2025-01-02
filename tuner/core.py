import logging

import spotipy
from tuner.encode import get_genre_vec
from tuner.db import (
    TunerMetadata,
    TunerOutput,
    get_pinecone_index,
    upload_genre_vector,
    search_for_matches,
    select_match,
)
from tuner.data import get_data

logger = logging.getLogger(__name__)


def tuner_match(sp: spotipy.Spotify) -> TunerOutput:
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
        return None

    logger.info("Printing result")
    score, match_metadata = select_match(matches)
    output = TunerOutput(match_metadata, user_metadata, score)

    return output


def tuner_delete(sp):
    user = sp.current_user()
    index = get_pinecone_index()
    index.delete(ids=[user["uri"]])
