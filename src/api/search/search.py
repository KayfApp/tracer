from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Query

router = APIRouter(
    prefix='/search',
)

@router.get("/")
async def search(query : str, top_n : int, providers : Annotated[list[str], Query()]):
    # perform local search if requested

    # perform server searches
 
    # merge all results and return top_n
    pass
