from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from database import Base
from datetime import datetime


class LoanMemberEmi(Base):
    __tablename__ = "loan_member_emi"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    emi_date = Column(DateTime, nullable=False)
    emi_amount = Column(Numeric(10, 2), nullable=False)
    emi_delay = Column(String(50), default='0', nullable=False)
    emi_status = Column(String(50), default='Pending', nullable=False)
    label = Column(String(50), default='Upcoming', nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    created_by = Column(String(255), default='System', nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)
