from __future__ import annotations
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from schema.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from schema.document.document import Document

class SubDocument(Base):
    __tablename__ = 'sub_documents'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    data: Mapped[str] = mapped_column(Text, nullable=False)
    document: Mapped["Document"] = relationship("Document", back_populates="sub_documents")
