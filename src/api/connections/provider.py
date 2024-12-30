from typing import Optional
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from globals import DB_SESSION
from provider.provider_list import mapping
from schema.connections.provider import Provider
from schema.connections.provider_instance import ProviderInstance
from provider.provider_instance_registry import ProviderInstanceRegistry

router = APIRouter(
    prefix='/connections/providers',
)

@router.get("/")
async def list_providers():
    with DB_SESSION() as session:   
        providers = session.query(Provider).all()
        return providers

@router.get("/{provider_id}/get-form")
async def get_provider_form(provider_id : str):
    with DB_SESSION() as session:   
        provider = session.query(Provider).filter_by(id=provider_id).first()
        if(provider != None):
            return provider.schema
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found.")

@router.get("/{provider_id}/instances")
async def list_instances(provider_id : str):
    with DB_SESSION() as session:   
        provider = session.query(Provider).filter_by(id=provider_id).first()
        if(provider != None):
            return provider.instances
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found.")

@router.put("/{provider_id}/add")
async def add_instance(provider_id : str, name : str, desc : str, data : dict):
    with DB_SESSION() as session:   
        provider = session.query(Provider).filter_by(id=provider_id).first()
        if(provider != None):
            instance = ProviderInstance(name=name, desc=desc, data=data, provider=provider)
            session.add(instance)
            session.commit()
            ProviderInstanceRegistry.instance().add(instance.id, mapping()[provider_id](instance.id))
        else:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found.")

@router.get("/{provider_instance_id}")
async def instance_info(provider_instance_id : int):
    with DB_SESSION() as session:
        instance = session.query(ProviderInstance).filter_by(id=provider_instance_id).first()
        if(instance != None):
            return instance
        raise HTTPException(status_code=404, detail=f"Provider instance {provider_instance_id} not found.")
        
@router.post("/{provider_instance_id}/update")
async def update_instance(provider_instance_id : int, name : Optional[str], desc : Optional[str]):
    with DB_SESSION() as session:
        instance = session.query(ProviderInstance).filter_by(id=provider_instance_id).first()
        if(instance != None):
            if(name != None):
                instance.name = name
            if(desc != None):
               instance.desc = desc
            session.commit()
        else:
            raise HTTPException(status_code=404, detail=f"Provider instance {provider_instance_id} not found.")

@router.delete("/{provider_instance_id}/remove")
async def remove_instance(provider_instance_id : int):
    with DB_SESSION() as session:
        instance = session.query(ProviderInstance).filter_by(id=provider_instance_id).first()
        if(instance != None):
            ProviderInstanceRegistry.instance().remove(provider_instance_id)
            session.delete(instance)
            session.commit()
        else:
            raise HTTPException(status_code=404, detail=f"Provider instance {provider_instance_id} not found.")
