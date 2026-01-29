from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MemberBase(BaseModel):
    full_name: str
    father_spouse_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    place: Optional[str] = None
    adhar_number: Optional[str] = None
    pan_number: Optional[str] = None
    customer_photo: Optional[str] = None
    primary_mobile_number: str
    alternate_contact_number: Optional[str] = None
    email_address: Optional[str] = None
    current_address: Optional[str] = None
    pincode: Optional[str] = None
    residence_type: Optional[str] = None
    years_at_current_residence: Optional[int] = None
    permanent_address: Optional[str] = None
    occupation_type: Optional[str] = None
    employer_business_name: Optional[str] = None
    work_address: Optional[str] = None
    designation: Optional[str] = None
    monthly_gross_income: Optional[float] = None
    monthly_net_income: Optional[float] = None
    total_work_experience: Optional[str] = None
    existing_active_loans: Optional[int] = None
    total_monthly_emi: Optional[float] = None
    number_of_dependents: Optional[int] = None
    account_holder_name: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None
    guarantor_name: Optional[str] = None
    guarantor_relationship: Optional[str] = None
    guarantor_contact_number: Optional[str] = None
    guarantor_kyc_id: Optional[str] = None


class MemberCreate(MemberBase):
    created_by: str


class MemberUpdate(BaseModel):
    full_name: Optional[str] = None
    father_spouse_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    place: Optional[str] = None
    adhar_number: Optional[str] = None
    pan_number: Optional[str] = None
    customer_photo: Optional[str] = None
    primary_mobile_number: Optional[str] = None
    alternate_contact_number: Optional[str] = None
    email_address: Optional[str] = None
    current_address: Optional[str] = None
    pincode: Optional[str] = None
    residence_type: Optional[str] = None
    years_at_current_residence: Optional[int] = None
    permanent_address: Optional[str] = None
    occupation_type: Optional[str] = None
    employer_business_name: Optional[str] = None
    work_address: Optional[str] = None
    designation: Optional[str] = None
    monthly_gross_income: Optional[float] = None
    monthly_net_income: Optional[float] = None
    total_work_experience: Optional[str] = None
    existing_active_loans: Optional[int] = None
    total_monthly_emi: Optional[float] = None
    number_of_dependents: Optional[int] = None
    account_holder_name: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None
    guarantor_name: Optional[str] = None
    guarantor_relationship: Optional[str] = None
    guarantor_contact_number: Optional[str] = None
    guarantor_kyc_id: Optional[str] = None
    updated_by: Optional[str] = None


class MemberResponse(MemberBase):
    id: int
    status: str
    del_mark: str
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
