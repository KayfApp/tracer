from __future__ import annotations
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from schema.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from schema.connections.provider_instance import ProviderInstance
    from schema.document.sub_document import SubDocument

class Document(Base):
    __tablename__ = 'documents'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_instance_id: Mapped[int] = mapped_column(Integer, ForeignKey('provider_instances.id', ondelete='CASCADE'), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text)
    author_avatar: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[DateTime] = mapped_column(DateTime)
    origin: Mapped["ProviderInstance"] = relationship("ProviderInstance", back_populates="documents")
    sub_documents: Mapped[list["SubDocument"]] = relationship(
        "SubDocument", back_populates="document", cascade="all, delete-orphan"
    )
