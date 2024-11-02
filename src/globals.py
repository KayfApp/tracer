from sentence_transformers import SentenceTransformer

EMBEDDING_ENCODER = SentenceTransformer("all-mpnet-base-v2")
EMBEDDING_DIMS = 768
