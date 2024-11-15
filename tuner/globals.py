SCOPE = [
    "user-top-read",
    # "user-read-recently-played",  # Is there a way to use this?
]

ONNX_PATH = "./data/artifacts/model.onnx"

MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_REPO = "sentence-transformers"
REVISION = "fa97f6e7cb1a59073dff9e6b13e2715cf7475ac9"

MODEL_PATH = f"{MODEL_REPO}/{MODEL_NAME}"

PINECONE_HOST = (
    "https://tuner-genre-vecs-all-minilm-l6-v2-w50ynqp.svc.aped-4627-b74a.pinecone.io"
)
