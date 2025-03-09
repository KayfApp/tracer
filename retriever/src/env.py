import os

# EMBEDDINGS
EMBEDDING_DIMS = 768
EMBEDDING_TOKEN_LIMIT = 1024

# DATABASE
PSQL_URL = os.getenv("PSQL_URL", "localhost")
PSQL_PORT = os.getenv("PSQL_PORT", "5432")
PSQL_USERNAME = os.getenv("PSQL_USERNAME", "postgres")
PSQL_PASSWORD = os.getenv("PSQL_PASSWORD", "admin")
PSQL_DB = os.getenv("PSQL_DB", "tracer")

# PATHS

HOME_DIR = os.path.expanduser("~")
CACHE_PATH = os.getenv("CACHE_PATH", os.path.join(HOME_DIR, ".cache", "kayf", "tracer"))
LOGGING_PATH = f"{CACHE_PATH}/logs"

# FETCHING TIME IN SECONDS -> how long wait until next fetch
FETCHING_TIME = 60

# HOW MANY THREADS SHOULD FETCH PROVIDER INSTANCES
FETCHING_THREADS = 5
