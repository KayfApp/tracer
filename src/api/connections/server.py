from fastapi import APIRouter

router = APIRouter(
    prefix='/connections/servers',
)

@router.get("/")
async def list_servers():
    pass

@router.put("/add")
async def add_server():
    pass

@router.delete("/{server_id}/remove")
async def remove_server():
    pass
