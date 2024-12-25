from sqlalchemy import Column, Integer, String, Text, JSONB
from sqlalchemy.orm import relationship

from schema.base import Base

class BaseProvider(Base):
    __tablename__ = 'providers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    desc = Column(String(500))
    avatar = Column(Text)
    schema = Column(JSONB) # data schema required to load @provider_instances
    instances = relationship("ProviderInstance", back_populates="provider", cascade="all, delete-orphan")
