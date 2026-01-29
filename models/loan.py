from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from datetime import datetime
from database import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(String(255), nullable=False, unique=True, index=True)
    member_group_id = Column(Integer, ForeignKey("members_groups.id"), nullable=True)
    application_date = Column(Date, nullable=True)
    loan_amount = Column(Float, nullable=False)
    loan_type = Column(String(100), nullable=True)
    interest_rate = Column(Float, nullable=True)
    interest_amount = Column(Float, nullable=True)
    loan_tenure = Column(Integer, nullable=True)
    monthly_emi = Column(Float, nullable=True)
    emi_day = Column(String(50), nullable=True)
    loan_start_date = Column(Date, nullable=True)
    repayment_frequency = Column(String(50), nullable=True)
    processing_fees = Column(Float, nullable=True)
    insurance_fees = Column(Float, nullable=True)
    other_fees = Column(Float, nullable=True)
    field_officer_id = Column(String(255), nullable=True)
    visit_date = Column(DateTime, nullable=True)
    geo_tagging = Column(String(255), nullable=True)
    business_asset_verification = Column(Text, nullable=True)
    cash_flow_analysis = Column(Text, nullable=True)
    credit_officer_comments = Column(Text, nullable=True)
    verification_status = Column(String(50), nullable=True)
    loan_status = Column(String(50), default='Draft', nullable=False)
    status = Column(String(1), default='A', nullable=False)
    del_mark = Column(String(1), default='N', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(255), nullable=True)
    assign_to = Column(String(255), nullable=True)
