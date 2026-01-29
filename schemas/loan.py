from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, date


class LoanBase(BaseModel):
    loan_id: str
    member_group_id: Optional[int] = None
    application_date: Optional[date] = None
    loan_amount: float
    loan_type: Optional[str] = None
    interest_rate: Optional[float] = None
    interest_amount: Optional[float] = None
    loan_tenure: Optional[int] = None
    monthly_emi: Optional[float] = None
    emi_day: str
    loan_start_date: Optional[date] = None
    repayment_frequency: Optional[str] = None
    processing_fees: Optional[float] = None
    insurance_fees: Optional[float] = None
    other_fees: Optional[float] = None
    field_officer_id: Optional[str] = None
    visit_date: Optional[datetime] = None
    geo_tagging: Optional[str] = None
    business_asset_verification: Optional[str] = None
    cash_flow_analysis: Optional[str] = None
    credit_officer_comments: Optional[str] = None
    verification_status: Optional[str] = None
    loan_status: Optional[str] = None
    assign_to: Optional[str] = None

    @field_validator('visit_date', mode='before')
    @classmethod
    def set_visit_date(cls, v):
        if v is None or v == '' or v == 'null':
            return datetime.now()
        return v


class LoanCreate(LoanBase):
    created_by: str


class LoanUpdate(BaseModel):
    loan_id: Optional[str] = None
    member_group_id: Optional[int] = None
    application_date: Optional[date] = None
    loan_amount: Optional[float] = None
    loan_type: Optional[str] = None
    interest_rate: Optional[float] = None
    interest_amount: Optional[float] = None
    loan_tenure: Optional[int] = None
    monthly_emi: Optional[float] = None
    emi_day: Optional[str] = None
    loan_start_date: Optional[date] = None
    repayment_frequency: Optional[str] = None
    processing_fees: Optional[float] = None
    insurance_fees: Optional[float] = None
    other_fees: Optional[float] = None
    field_officer_id: Optional[str] = None
    visit_date: Optional[datetime] = None
    geo_tagging: Optional[str] = None
    business_asset_verification: Optional[str] = None
    cash_flow_analysis: Optional[str] = None
    credit_officer_comments: Optional[str] = None
    verification_status: Optional[str] = None
    loan_status: Optional[str] = None
    assign_to: Optional[str] = None
    updated_by: Optional[str] = None

    @field_validator('visit_date', mode='before')
    @classmethod
    def set_visit_date(cls, v):
        if v is None or v == '' or v == 'null':
            return datetime.now()
        return v


class LoanResponse(LoanBase):
    id: int
    status: str
    del_mark: str
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
