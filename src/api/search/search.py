from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Query

router = APIRouter(
    prefix='/search',
)

@router.get("/")
async def search(query : str, providers : Annotated[list[str], Query()]):
    pass
