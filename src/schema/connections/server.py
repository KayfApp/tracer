from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase

class Server(DeclarativeBase):
    __tablename__ = 'servers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    desc = Column(String(500))
    url = Column(Text)
