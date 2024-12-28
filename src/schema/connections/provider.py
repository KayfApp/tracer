from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schema.base import Base

class Provider(Base):
    __tablename__ = 'providers'
    
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    desc: Mapped[str] = mapped_column(String(500))
    avatar: Mapped[str] = mapped_column(Text)
    schema: Mapped[dict] = mapped_column(JSON)  # Data schema required to load @provider_instances
    instances: Mapped[list["ProviderInstance"]] = relationship(
        "ProviderInstance", back_populates="provider", cascade="all, delete-orphan"
    )
