from contextlib import asynccontextmanager
from env import LOGGING_PATH
from globals import LOGGER
from indexing.clustering_queue import ClusteringQueue
from indexing.indexing_queue import IndexingQueue
from provider.provider_list import load_providers
from fastapi import FastAPI
from api.connections.provider import router as provider_router
from api.connections.server import router as server_router
from api.search.exploration import router as exploration_router
from api.search.search import router as search_router
from provider.provider_queue import ProviderQueue
from datetime import datetime
import logging
import os

# +==================================================+
# |  _  __     _     __   __  _____                  |
# | | |/ /    / \    \ \ / / |  ___|                 |
# | | ' /    / _ \    \ V /  | |_                    |
# | | . \   / ___ \    | |   |  _|                   |
# | |_|\_\ /_/   \_\   |_|   |_|                     |
# |                                                  |
# |  _____   ____       _       ____   _____   ____  |
# | |_   _| |  _ \     / \     / ___| | ____| |  _ \ |
# |   | |   | |_) |   / _ \   | |     |  _|   | |_) ||
# |   | |   |  _ <   / ___ \  | |___  | |___  |  _ < |
# |   |_|   |_| \_\ /_/   \_\  \____| |_____| |_| \_\|
# |                                                  |
# +==================================================+


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(LOGGING_PATH):
        try:
            os.makedirs(LOGGING_PATH)
        except PermissionError:
            print("Can't create directory for log files due to lacking permissions!")

    # Create a logger
    logger = LOGGER
    logger.setLevel(logging.INFO)  # Set the base logging level for the logger

    # Create a console handler for all logs (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Handle INFO and above
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    # Create a file handler for error logs only
    file_handler = logging.FileHandler(f"{LOGGING_PATH}/{datetime.now().strftime('%H_%M_%d_%m_%Y')}.log")
    file_handler.setLevel(logging.ERROR)  # Handle ERROR and above
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Disable access and ASGI logs from uvicorn
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.asgi").disabled = True
    
    ProviderQueue.instance().start()
    IndexingQueue.instance().start()
    ClusteringQueue.instance().start()
    load_providers()
    yield
    ProviderQueue.instance().stop()

app = FastAPI(lifespan=lifespan)

app.include_router(provider_router)
app.include_router(server_router)
app.include_router(exploration_router)
app.include_router(search_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8080)
