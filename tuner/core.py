import logging
import os

from tuner.globals import ONNX_PATH
from tuner.encode import get_genre_vec, encode_genres
from tuner.download import download_model
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
    user, artists, genres = get_data(sp)

    if not os.path.exists(ONNX_PATH):
        logger.info("Model not found, downloading")
        download_model()

    # Get genre embeddings
    logger.info("Embedding genres")
    embeddings = encode_genres(genres)
    genre_vec = get_genre_vec(genres, embeddings)

    # Log to database
    logger.info("Logging to database")
    index = get_pinecone_index()
    upload_genre_vector(index, user, genre_vec, genres, artists)

    # Get other users
    logger.info("Searching for matches")
    matches = search_for_matches(index, user, genre_vec)

    if not matches:
        logger.warning("No matches found")
        return None, [], [], []

    logger.info("Printing result")
    match = select_match(matches)
    shared_genres, shared_artists, recommended_artists = match_overlap(
        match,
        genres,
        artists,
    )
    return match, shared_genres, shared_artists, recommended_artists
