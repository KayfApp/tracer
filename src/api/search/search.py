from fastapi import APIRouter

router = APIRouter(
    prefix='/search',
)

@router.get("/")
async def search():
    """Perform search with given parameters for specified sub-corpus"""
    pass
