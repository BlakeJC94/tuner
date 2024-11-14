# How to generate embeddings?

# %%
# Example genres

# data_path = "./data/genres.txt"
# with open(data_path, "r") as f:
#     data = [l.strip() for l in f.readlines()]

genres = [
    "Alternative Rock",
    "Alternative Pop Rock",
    "Rock",
    "Hip Hop",
    "Rap",
    "Rap Metal",
    "Metalcore",
]

# %%
# Load model
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# %%
# Get embeddings for each genre
embeddings = {
    g: model.encode(g).reshape(1, -1) for g in genres
}

# %%
# Compare genres
from sklearn.metrics.pairwise import cosine_similarity

pairs = [
    (genres[0], genres[1]),
    (genres[0], genres[2]),
    (genres[2], genres[3]),
    (genres[3], genres[4]),
    (genres[4], genres[5]),
    (genres[5], genres[6]),
    (genres[5], genres[1]),
]

for (g1, g2) in pairs:
    result = cosine_similarity(embeddings[g1], embeddings[g2])[0][0]
    print(f"Similarity between {g1} and {g2}: {result:.2f}")

# %%
# Compare music taste of 3 hypothetical people
import numpy as np

people = [
    {  # Alt-rock fan
        genres[2]: 10,
        genres[0]: 5,
        genres[1]: 3,
    },
    {  # Rap fan
        genres[3]: 9,
        genres[4]: 6,
    },
    {  # Rap/Metal fan
        genres[5]: 7,
        genres[6]: 6,
        genres[3]: 6,
        genres[0]: 5,
    },
]

def music_taste_vector(genre_counts, embeddings):
    weighted_embeddings = np.zeros_like(list(embeddings.values())[0])
    for genre, count in genre_counts.items():
        weighted_embeddings += embeddings[genre] * count
    return weighted_embeddings / np.linalg.norm(weighted_embeddings)

vectors = [music_taste_vector(p, embeddings) for p in people]

pairs = [
    (0, 1),  # Alt-rock and Rap
    (0, 2),  # Rap and Rap metal
    (1, 2),  # Alt rock and rap metal
]
for (idx1, idx2) in pairs:
    result = cosine_similarity(vectors[idx1], vectors[idx2])[0][0]
    print(f"Similarity between {idx1} and {idx2}: {result:.2f}")

# %%
# place in pinecone
from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

index = pc.Index(host="https://tuner-genre-vecs-all-minilm-l6-v2-w50ynqp.svc.aped-4627-b74a.pinecone.io")

index.upsert(
  vectors=[
    {"id": name, "values": vec[0].tolist()} for name, vec in zip(("A", "B", "C"), vectors)
  ]
)

