
from fastapi import APIRouter

router = APIRouter(
    prefix='/connections/providers',
)

@router.get("/")
async def list_providers():
    """List all available providers that can be added"""
    pass

@router.get("/{provider_id}/get-form")
async def get_provider_form():
    """Get input form schema for provider"""
    pass

@router.get("/instances")
async def list_providers_instances():
    """List all added provider instances"""
    pass


@router.put("/add")
async def add_provider_instance():
    """Add provider instance"""
    pass

@router.delete("/{provider_instance_id}/remove")
async def remove_provider_instance():
    """Remove provider instance"""
    pass
