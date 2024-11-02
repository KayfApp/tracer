from fastapi import APIRouter

router = APIRouter(
    prefix='/',
)

@router.get("/")
async def list_servers():
    pass
