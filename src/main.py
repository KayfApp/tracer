from contextlib import asynccontextmanager
from env import LOGGING_PATH
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

############
##  KAYF  ##
## TRACER ##
############

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(LOGGING_PATH):
        try:
            os.makedirs(LOGGING_PATH)
        except PermissionError:
            print("Can't create directory for log files due to lacking permissions!")
    logging.basicConfig(filename=f"{LOGGING_PATH}/{datetime.now().strftime("%H_%M_%d_%m_%Y")}.log", level=logging.INFO)
    load_providers()
    ProviderQueue.instance().start()
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
