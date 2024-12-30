import logging

import numpy as np

from tuner.globals import NPY_PATH
from tuner.utils import get_all_genres

logger = logging.getLogger(__name__)


def get_genre_vec(data) -> list[float]:
    all_genres = get_all_genres()
    all_embeddings = np.load(NPY_PATH)

    weighted_embeddings = np.zeros((1, all_embeddings.shape[-1]))
    for genre, count in data.genres:
        if genre not in all_genres:
            logger.error(f"'{genre}' not in vector table")
            continue
        genre_idx = all_genres.index(genre)
        embedding = all_embeddings[genre_idx, :].reshape(1, -1)
        weighted_embeddings += embedding * count

    weighted_embeddings = weighted_embeddings / np.linalg.norm(weighted_embeddings)
    return weighted_embeddings[0].tolist()
