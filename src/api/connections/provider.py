from typing import Optional
from fastapi import APIRouter

router = APIRouter(
    prefix='/connections/providers',
)

@router.get("/")
async def list_providers():
    pass

@router.get("/{provider_id}/get-form")
async def get_provider_form(provider_id : int):
    pass

@router.get("/{provider_id}/instances")
async def list_instances(provider_id : int):
    pass

@router.put("/{provider_id}/add")
async def add_instance(provider_id : int, name : str, desc : str, data : str):
    pass

@router.get("/{provider_instance_id}")
async def instance_info(provider_instance_id : int):
    pass

@router.post("/{provider_instance_id}/update")
async def update_instance(provider_instance_id : int, name : Optional[str], desc : Optional[str]):
    pass

@router.delete("/{provider_instance_id}/remove")
async def remove_instance(provider_instance_id : int):
    pass
