import numpy as np
import onnxruntime as ort

from tuner.globals import ONNX_PATH, MODEL_PATH, REVISION
from transformers import AutoTokenizer


def encode_genres(genres):
    ort_session = ort.InferenceSession(ONNX_PATH)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, revision=REVISION)

    embeddings = {}
    for genre, _ in genres:
        inputs = tokenizer(genre, return_tensors="np")
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]

        # Run inference on the ONNX model
        onnx_outputs = ort_session.run(
            None,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
            },
        )

        # Pool the outputs (average pooling for sentence embedding)
        last_hidden_state = onnx_outputs[0]
        pooled_output = np.mean(last_hidden_state, axis=1)
        embeddings[genre] = pooled_output[0].reshape(1, -1)

    return embeddings


def get_genre_vec(
    genre_counts: list[tuple[str, int]],
    embeddings: dict[str, np.ndarray],
) -> np.ndarray:
    weighted_embeddings = np.zeros_like(list(embeddings.values())[0])
    for genre, count in genre_counts:
        weighted_embeddings += embeddings[genre] * count

    weighted_embeddings = weighted_embeddings / np.linalg.norm(weighted_embeddings)
    return weighted_embeddings[0].tolist()
