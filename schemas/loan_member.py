from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class LoanMemberBase(BaseModel):
    loan_id: int
    member_group_id: int
    member_id: int
    name: str
    place: Optional[str] = None
    phone: Optional[str] = None
    amount: Decimal


class LoanMemberCreate(LoanMemberBase):
    created_by: str


class LoanMemberResponse(LoanMemberBase):
    id: int
    created_at: datetime
    created_by: str
    collected: Decimal
    pending: Decimal

    class Config:
        from_attributes = True
