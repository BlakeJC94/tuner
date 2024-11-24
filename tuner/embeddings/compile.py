import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from tuner.globals import NPY_PATH, MODEL_NAME, REVISION
from tuner.utils import get_all_genres


def compile_embeddings():
    genres = get_all_genres()

    model = SentenceTransformer(MODEL_NAME, revision=REVISION)
    embeddings = [model.encode(g).reshape(1, -1) for g in genres]
    embeddings = np.concatenate(embeddings, axis=0)

    np.save(NPY_PATH, embeddings)
