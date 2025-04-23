from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import uvicorn

app = FastAPI(
    title="Sentence-BERT API",
    description="FastAPI app for Sentence-BERT embedding and tokenization",
    version="1.1.0"
)

# Load models
model_name = "sentence-transformers/paraphrase-MiniLM-L12-v2"
model = SentenceTransformer(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# === Schemas ===
class Document(BaseModel):
    id: str
    content: str

class EmbeddingResponse(BaseModel):
    id: str
    vector: List[float]

class TokenizationResponse(BaseModel):
    id: str
    input_ids: List[int]
    attention_mask: List[int]

# === Endpoints ===
@app.get("/", tags=["Health"])
def root():
    return {"message": "Sentence-BERT API is online."}

@app.post("/embed", response_model=List[EmbeddingResponse], tags=["Embedding"])
def embed(documents: List[Document]):
    texts = [doc.content for doc in documents]
    embeddings = model.encode(texts)

    return [
        EmbeddingResponse(id=doc.id, vector=emb.tolist())
        for doc, emb in zip(documents, embeddings)
    ]

@app.post("/tokenize", response_model=List[TokenizationResponse], tags=["Tokenization"])
def tokenize(documents: List[Document]):
    texts = [doc.content for doc in documents]
    tokens = tokenizer(texts, padding="max_length", truncation=True, return_tensors="pt")

    results = []
    for i, doc in enumerate(documents):
        results.append(TokenizationResponse(
            id=doc.id,
            input_ids=tokens["input_ids"][i].tolist(),
            attention_mask=tokens["attention_mask"][i].tolist()
        ))
    return results

@app.get("/metadata", tags=["Metadata"])
def get_metadata():
    return {
        "embedding_dimension": model.get_sentence_embedding_dimension()
    }

# === Auto-run if executed directly ===
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

