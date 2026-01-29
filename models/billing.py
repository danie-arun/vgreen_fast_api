from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric
from datetime import datetime
from database import Base


class Billing(Base):
    __tablename__ = "billing"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    member_group_id = Column(Integer, ForeignKey("members_groups.id"), nullable=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    billing_code = Column(String(50), nullable=False, index=True)
    type = Column(String(20), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=False)
