from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BillingCreate(BaseModel):
    loan_id: Optional[int] = None
    member_id: Optional[int] = None
    member_group_id: Optional[int] = None
    staff_id: Optional[str] = None
    amount: float
    billing_code: str
    type: str
    description: Optional[str] = None
    org: Optional[str] = None
    created_by: str = "System"


class BillingUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None


class BillingResponse(BaseModel):
    id: int
    loan_id: Optional[int]
    member_id: Optional[int]
    member_group_id: Optional[int]
    staff_id: Optional[str]
    amount: float
    billing_code: str
    type: str
    description: Optional[str]
    org: str
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True
