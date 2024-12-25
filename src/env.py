import os

# EMBEDDINGS
EMBEDDING_DIMS = 768

# DATABASE
PSQL_URL = "localhost"
PSQL_PORT = "5432"
PSQL_USERNAME = "postgres" 
PSQL_PASSWORD = "admin"
PSQL_DB = "tracer"

# PATHS
INDEX_PATH = f"/home/{os.getlogin()}/.cache/kayf/tracer/"

# INDEX SIZE (= how much ram/vram I want to use) in MB
MAX_INDEX_SIZE = 4096

# INDEXING TIME IN SECONDS
INDEXING_TIME = 60
