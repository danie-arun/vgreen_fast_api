from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StaffCreate(BaseModel):
    staff_id: str
    name: str
    email: str
    phone: str
    dob: Optional[str] = None
    gender: Optional[str] = None
    p_address: Optional[str] = None
    doj: Optional[str] = None
    designation: str
    reporting_to: Optional[str] = None
    branch: Optional[str] = None
    staff_status: Optional[str] = None
    department: str
    bank_ac: Optional[str] = None
    bank_ifsc: Optional[str] = None
    ac_holder_name: Optional[str] = None
    salary: Optional[float] = None
    epf_no: Optional[str] = None
    esi_no: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    ref_check: Optional[str] = None
    disbursement_target: Optional[float] = None
    collection_target: Optional[float] = None
    onboarding_target: Optional[str] = None


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    p_address: Optional[str] = None
    doj: Optional[str] = None
    designation: Optional[str] = None
    reporting_to: Optional[str] = None
    branch: Optional[str] = None
    staff_status: Optional[str] = None
    department: Optional[str] = None
    bank_ac: Optional[str] = None
    bank_ifsc: Optional[str] = None
    ac_holder_name: Optional[str] = None
    salary: Optional[float] = None
    epf_no: Optional[str] = None
    esi_no: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    ref_check: Optional[str] = None
    disbursement_target: Optional[float] = None
    collection_target: Optional[float] = None
    onboarding_target: Optional[str] = None
    updated_by: Optional[str] = None


class StaffResponse(BaseModel):
    id: int
    staff_id: str
    name: str
    email: str
    phone: str
    dob: Optional[str]
    gender: Optional[str]
    p_address: Optional[str]
    doj: Optional[str]
    designation: str
    reporting_to: Optional[str]
    branch: Optional[str]
    staff_status: Optional[str]
    department: str
    bank_ac: Optional[str]
    bank_ifsc: Optional[str]
    ac_holder_name: Optional[str]
    salary: Optional[float]
    epf_no: Optional[str]
    esi_no: Optional[str]
    id_type: Optional[str]
    id_number: Optional[str]
    ref_check: Optional[str]
    disbursement_target: Optional[float]
    collection_target: Optional[float]
    onboarding_target: Optional[str]
    status: str
    del_mark: str
    created_at: Optional[datetime]
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
