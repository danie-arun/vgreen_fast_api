from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from database import Base


class MemberGroup(Base):
    __tablename__ = "members_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(String(255), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    place = Column(String(255), nullable=True)
    member_ids = Column(JSON, nullable=True)
    status = Column(String(1), default='A', nullable=False)
    del_mark = Column(String(1), default='N', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(255), nullable=True)
