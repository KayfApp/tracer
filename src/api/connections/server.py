from fastapi import APIRouter

router = APIRouter(
    prefix='/connections/servers',
)

@router.get("/")
async def list_servers():
    pass

@router.put("/add")
async def add_server(name : str, desc : str, url : str):
    pass

@router.get("/{server_id}")
async def server_info(server_id : int):
    pass

@router.post("/{server_id}/update")
async def update_server(server_id : int, name : str, desc : str):
    pass

@router.delete("/{server_id}/remove")
async def remove_server(server_id : int):
    pass
