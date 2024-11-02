from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship

class ProviderInstance(DeclarativeBase):
    __tablename__ = 'provider_instances'
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey('providers.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100))
    desc = Column(String(500))
    last_indexed = Column(DateTime)
    data = Column(JSONB) # schema has to be equal to @BaseProvider.input_data
    provider = relationship("BaseProvider", back_populates="instances")
    documents = relationship("Document", back_populates="origin")
