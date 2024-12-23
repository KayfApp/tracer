from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from env import PSQL_DB, PSQL_PASSWORD, PSQL_PORT, PSQL_URL, PSQL_USERNAME
from schema.base import Base

## SBERT / EMBEDDINGS ##

EMBEDDING_ENCODER = SentenceTransformer("all-mpnet-base-v2")
EMBEDDING_DIMS = 768

## DB ##

DB_ENGINE = create_engine(f"postgresql+psycopg://{PSQL_USERNAME}:{PSQL_PASSWORD}@{PSQL_URL}:{PSQL_PORT}/{PSQL_DB}")
Base.metadata.create_all(DB_ENGINE)
DB_SESSION = sessionmaker(bind = DB_ENGINE)
DB_SESSION = DB_SESSION()
