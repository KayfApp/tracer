from contextlib import asynccontextmanager
from env import LOGGING_PATH
from globals import LOGGER
from provider.provider_list import load_providers
from fastapi import FastAPI
from api import router
from provider.provider_queue import ProviderQueue
from datetime import datetime
import logging
import os
import nltk

nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

# KAYF TRACER DATA RETRIEVER

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
    file_handler = logging.FileHandler(f"{LOGGING_PATH}/{datetime.now().strftime('%Y%m%d%H%M')}.log")
    file_handler.setLevel(logging.ERROR)  # Handle ERROR and above
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Disable access and ASGI logs from uvicorn
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.asgi").disabled = True
    
    ProviderQueue.instance().start()
    load_providers()
    yield
    ProviderQueue.instance().stop()

app = FastAPI(lifespan=lifespan)

app.include_router(router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
