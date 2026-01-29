from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    org = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True, unique=True, index=True)
    role = Column(String(45), nullable=True)
    user_pass = Column(String(255), nullable=True)
    api_key = Column(String(255), nullable=True, unique=True, index=True)
    last_active = Column(DateTime, nullable=True)
    status = Column(String(2), nullable=True)
    del_mark = Column(String(2), nullable=True)
    date_created = Column(DateTime, nullable=True)
    date_updated = Column(DateTime, nullable=True)
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
