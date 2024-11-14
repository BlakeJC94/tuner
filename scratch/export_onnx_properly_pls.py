# %% Define test data

genres = [
    "Alternative Rock",
    "Alternative Pop Rock",
    "Rock",
    "Hip Hop",
    "Rap",
    "Rap Metal",
    "Metalcore",
]

MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_REPO = "sentence-transformers"
REVISION = "fa97f6e7cb1a59073dff9e6b13e2715cf7475ac9"

MODEL_PATH =f"{MODEL_REPO}/{MODEL_NAME}"

# %% Load native model and get embeddings
from sentence_transformers import SentenceTransformer


def get_native_embeddings(genres):
    model = SentenceTransformer(MODEL_NAME, revision=REVISION)
    embeddings = [model.encode(g) for g in genres]
    return embeddings


native_embeddings = get_native_embeddings(genres)

# %% Load native model and export to Onnx
from transformers import AutoModel, AutoTokenizer
from pathlib import Path
import torch

# Set the file path for the exported model
onnx_path = Path("model.onnx")


def export_native_to_onnx(genres, onnx_path):

    # Load the same underlying model and tokenizer
    transformer_model = AutoModel.from_pretrained(MODEL_PATH, revision=REVISION)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, revision=REVISION)

    # Prepare a sample input for ONNX export (a dummy input is necessary)
    text = genres[0]
    inputs = tokenizer(text, return_tensors="pt")

    # Export the model to ONNX format
    torch.onnx.export(
        transformer_model,
        (inputs["input_ids"], inputs["attention_mask"]),
        onnx_path,
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "last_hidden_state": {0: "batch_size", 1: "sequence_length"},
        },
        opset_version=14,
    )


export_native_to_onnx(genres, onnx_path)

# %% Import ONNX model and get embeddings
import onnxruntime as ort
import numpy as np


def get_onnx_embeddings(genres, onnx_path):
    ort_session = ort.InferenceSession(str(onnx_path))
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

    embeddings = []
    for text in genres:
        inputs = tokenizer(text, return_tensors="np")
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
        embeddings.append(pooled_output[0])

    return embeddings


onnx_embeddings = get_onnx_embeddings(genres, onnx_path)


# %% Compare results
def compare_results(genres, native_embeddings, onnx_embeddings):
    for genre, original_embedding, onnx_embedding in zip(
        genres,
        native_embeddings,
        onnx_embeddings,
    ):
        # Check the similarity between the embeddings (cosine similarity)
        cos_sim = np.dot(original_embedding, onnx_embedding) / (
            np.linalg.norm(original_embedding) * np.linalg.norm(onnx_embedding)
        )
        print(f"Cosine similarity for {genre}: {cos_sim:.4f}")


compare_results(genres, native_embeddings, onnx_embeddings)
