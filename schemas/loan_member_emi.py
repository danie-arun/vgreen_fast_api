from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional


class LoanMemberEmiBase(BaseModel):
    loan_id: int
    member_id: int
    emi_date: datetime
    emi_amount: Decimal
    emi_delay: str = '0'
    emi_status: str = 'Pending'


class LoanMemberEmiCreate(LoanMemberEmiBase):
    created_by: str


class LoanMemberEmiUpdate(BaseModel):
    emi_delay: Optional[str] = None
    emi_status: Optional[str] = None
    updated_by: Optional[str] = None


class LoanMemberEmiResponse(LoanMemberEmiBase):
    id: int
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: Optional[str]

    class Config:
        from_attributes = True
