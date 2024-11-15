import numpy as np

from sentence_transformers import SentenceTransformer
from pytest import fixture

from tuner.globals import (
    MODEL_NAME,
    REVISION,
)
from tuner.encode import encode_genres


@fixture
def genres():
    return [
        ("Alternative Rock", 1),
        ("Alternative Pop Rock", 3),
        ("Rock", 5),
        ("Hip Hop", 7),
        ("Rap", 9),
        ("Rap Metal", 11),
        ("Metalcore", 13),
    ]


def get_native_embeddings(genres):
    model = SentenceTransformer(MODEL_NAME, revision=REVISION)
    embeddings = {g: model.encode(g).reshape(1, -1) for g, _ in genres}
    return embeddings


def test_encode_genres(genres):
    native_embeddings = get_native_embeddings(genres)
    onnx_embeddings = encode_genres(genres)

    results = {}
    for genre, _ in genres:
        native_embedding = native_embeddings[genre][0]
        onnx_embedding = onnx_embeddings[genre][0]

        # Check the similarity between the embeddings (cosine similarity)
        results[genre] = np.dot(native_embedding, onnx_embedding) / (
            np.linalg.norm(native_embedding) * np.linalg.norm(onnx_embedding)
        )

    for k, v in results.items():
        assert abs(v - 1) < 1e-6, f"Mismatch in similarity for '{k}': {v:.4f}"
