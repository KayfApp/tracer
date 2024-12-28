from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from schema.base import Base

class Server(Base):
    __tablename__ = 'servers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    desc: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(Text)
