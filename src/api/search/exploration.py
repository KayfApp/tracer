from fastapi import APIRouter

router = APIRouter(
    prefix='/search/exploration',
)


@router.get("/{server_id}")
async def get_statistics():
    """Get corpus statistics (server summary) of current server"""
    pass

@router.get("/{server_id}/get-providers")
async def get_providers():
    """Get server provider list (for server summary) of current server"""
    pass
