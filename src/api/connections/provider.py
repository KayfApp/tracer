from fastapi import APIRouter

router = APIRouter(
    prefix='/connections/providers',
)

@router.get("/")
async def list_providers():
    pass

@router.get("/instances")
async def list_providers_instances():
    pass

@router.put("/add")
async def add_provider_instance():
    pass

@router.delete("/remove")
async def remove_provider_instance():
    pass
