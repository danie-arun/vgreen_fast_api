from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric
from datetime import datetime
from database import Base


class LoanMember(Base):
    __tablename__ = "loan_members"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    member_group_id = Column(Integer, ForeignKey("members_groups.id"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    place = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    collected = Column(Numeric(10, 2), nullable=False)
    pending = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=False)
