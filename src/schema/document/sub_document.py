from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from src.schema.base import Base

class SubDocument(Base):
    __tablename__ = 'sub_documents'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    data = Column(Text, nullable=False)
    document = relationship("Document", back_populates="sub_documents")
