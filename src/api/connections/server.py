from typing import Optional
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from schema.connections.server import Server

from globals import DB_SESSION

router = APIRouter(
    prefix='/connections/servers',
)

@router.get("/")
async def list_servers():
    with DB_SESSION() as session:   
        servers = session.query(Server).all()
        return servers

@router.put("/add")
async def add_server(name : str, desc : str, url : str):
    with DB_SESSION() as session:   
        server = Server(name=name, desc=desc, url=url)
        session.add(server)
        session.commit()

@router.get("/{server_id}")
async def server_info(server_id : int):
    with DB_SESSION() as session:
        server = session.query(Server).filter_by(id=server_id).first()
        return server

@router.post("/{server_id}/update")
async def update_server(server_id : int, name : Optional[str], desc : Optional[str]):
    with DB_SESSION() as session:
        server = session.query(Server).filter_by(id=server_id).first()
        if(server != None):
            if(name != None):
                server.name = name
            if(desc != None):
               server.desc = desc
            session.commit()
        else:
            raise HTTPException(status_code=404, detail=f"Server {server_id} not found.")


@router.delete("/{server_id}/remove")
async def remove_server(server_id : int):
    with DB_SESSION() as session:
        server = session.query(Server).filter_by(id=server_id).first()
        if(server != None):
            session.delete(server)
            session.commit()
        else:
            raise HTTPException(status_code=404, detail=f"Server {server_id} not found.")
