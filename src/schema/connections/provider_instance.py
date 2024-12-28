from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schema.base import Base
from schema.document.document import Document

class ProviderInstance(Base):
    __tablename__ = 'provider_instances'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_id: Mapped[str] = mapped_column(String(100), ForeignKey('providers.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(100))
    desc: Mapped[str] = mapped_column(String(500))
    last_indexed: Mapped[datetime] = mapped_column(DateTime)
    data: Mapped[dict] = mapped_column(JSON)  # schema has to be equal to @Provider.input_data
    provider: Mapped["Provider"] = relationship("Provider", back_populates="instances")
    documents: Mapped[list[Document]] = relationship("Document", back_populates="origin")
