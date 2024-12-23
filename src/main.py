from fastapi import FastAPI
from api.connections.provider import router as provider_router
from api.connections.server import router as server_router
from api.connections.provider import router as exploration_router
from api.connections.provider import router as search_router

app = FastAPI()

app.include_router(provider_router)
app.include_router(server_router)
app.include_router(exploration_router)
app.include_router(search_router)

if __name__ == '__main__':
   import uvicorn
   uvicorn.run("main:app", host="localhost", port=8080)
