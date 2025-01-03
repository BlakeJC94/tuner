SCOPE = [
    "user-top-read",
    "playlist-modify-public",
    # "user-read-recently-played",  # Is there a way to use this?
]

ONNX_PATH = "./data/artifacts/model.onnx"
GENRES_PATH = "./data/genres.txt"
NPY_PATH = "./data/embeddings.npy"

MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_REPO = "sentence-transformers"
REVISION = "fa97f6e7cb1a59073dff9e6b13e2715cf7475ac9"

MODEL_PATH = f"{MODEL_REPO}/{MODEL_NAME}"

PINECONE_HOST = (
    "https://tuner-genre-vecs-all-minilm-l6-v2-w50ynqp.svc.aped-4627-b74a.pinecone.io"
)
