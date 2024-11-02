from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship

class Document(DeclarativeBase):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    provider_instance_id = Column(Integer, ForeignKey('provider_instances.id', ondelete='CASCADE'), nullable=False)
    id_in_provider = Column(Text)
    doc_type = Column(String(64))
    status = Column(String(64))
    title = Column(Text, Nullable=False)
    author = Column(Text)
    author_avatar = Column(Text)
    url = Column(Text)
    location = Column(Text)
    timestamp = Column(DateTime)
    origin = relationship("ProviderInstance", back_populates="documents")
    sub_documents = relationship("SubDocument", back_populates="document", cascade="all, delete-orphan")
