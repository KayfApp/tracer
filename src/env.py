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
CACHE_PATH = f"/home/{os.getlogin()}/.cache/kayf/tracer"
LOGGING_PATH = f"{CACHE_PATH}/logs"
INDEX_PATH = f"{CACHE_PATH}/index"

# INDEX SIZE (= how much ram/vram I want to use) in MB
MAX_INDEX_SIZE = 1024

# MEMORY DISTRIBUTION
MAX_MEMORY = 4096
MAX_INDEXING_MEMORY = 1024
MAX_CLUSTERING_MEMORY = 1024

# FETCHING TIME IN SECONDS -> how long wait until next fetch
FETCHING_TIME = 60

# INDEXING TIME IN SECONDS -> how long wait until next index
INDEXING_TIME = 300

# HOW MANY THREADS SHOULD INDEX PROVIDER INSTANCES
INDEXING_THREADS = 5


# NOTE: ASSERTS - DO NOT REMOVE

assert MAX_MEMORY - MAX_INDEX_SIZE - MAX_INDEXING_MEMORY - MAX_CLUSTERING_MEMORY > 0
