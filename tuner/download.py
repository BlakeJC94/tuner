import torch
from transformers import AutoModel, AutoTokenizer

from tuner.globals import (
    ONNX_PATH,
    REVISION,
    MODEL_PATH,
)


def download_model():
    # Load the same underlying model and tokenizer
    transformer_model = AutoModel.from_pretrained(MODEL_PATH, revision=REVISION)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, revision=REVISION)

    # Prepare a sample input for ONNX export (a dummy input is necessary)
    text = "Alternative Rock"
    inputs = tokenizer(text, return_tensors="pt")

    # Export the model to ONNX format
    torch.onnx.export(
        transformer_model,
        (inputs["input_ids"], inputs["attention_mask"]),
        ONNX_PATH,
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "last_hidden_state": {0: "batch_size", 1: "sequence_length"},
        },
        opset_version=14,
    )
