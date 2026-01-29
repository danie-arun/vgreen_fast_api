from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base

class Org(Base):
    __tablename__ = "org"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    org_type = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    client_id = Column(String(100), nullable=True, unique=True, index=True)
    api_token = Column(String(100), nullable=True)
    status = Column(String(45), nullable=True)
    del_mark = Column(String(45), nullable=True)
    date_created = Column(DateTime, nullable=True)
    date_updated = Column(DateTime, nullable=True)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
