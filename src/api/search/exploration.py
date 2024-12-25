from typing import Annotated
from fastapi import APIRouter, Query

router = APIRouter(
    prefix='/search/exploration',
)

@router.get("/")
async def get_statistics(providers : Annotated[list[str], Query()]):
    pass

@router.get("/get-providers")
async def get_local_providers():
    pass

@router.get("/get-all-providers")
async def get_all_providers():
    pass
