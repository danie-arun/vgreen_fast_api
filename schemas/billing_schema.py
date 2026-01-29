from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BillingCreate(BaseModel):
    loan_id: int
    member_id: int
    member_group_id: Optional[int] = None
    amount: float
    billing_code: str
    type: str
    description: Optional[str] = None
    created_by: str = "System"


class BillingUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None


class BillingResponse(BaseModel):
    id: int
    loan_id: int
    member_id: int
    member_group_id: Optional[int]
    amount: float
    billing_code: str
    type: str
    description: Optional[str]
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True
