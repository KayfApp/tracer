from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, JSONB
from sqlalchemy.orm import relationship

from schema.base import Base

class ProviderInstance(Base):
    __tablename__ = 'provider_instances'
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey('providers.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100))
    desc = Column(String(500))
    last_indexed = Column(TIMESTAMP)
    data = Column(JSONB) # schema has to be equal to @BaseProvider.input_data
    provider = relationship("BaseProvider", back_populates="instances")
    documents = relationship("Document", back_populates="origin")
