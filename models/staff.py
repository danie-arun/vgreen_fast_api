from sqlalchemy import Column, Integer, String, DateTime, Numeric
from database import Base
from datetime import datetime


class Staff(Base):
    __tablename__ = "staffs"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    dob = Column(String(45), nullable=True)
    gender = Column(String(45), nullable=True)
    p_address = Column(String(45), nullable=True)
    doj = Column(String(45), nullable=True)
    designation = Column(String(100), nullable=False)
    reporting_to = Column(String(255), nullable=True)
    branch = Column(String(255), nullable=True)
    staff_status = Column(String(255), nullable=True)
    department = Column(String(100), nullable=False)
    bank_ac = Column(String(255), nullable=True)
    bank_ifsc = Column(String(255), nullable=True)
    ac_holder_name = Column(String(255), nullable=True)
    salary = Column(Numeric(10, 2), nullable=True)
    epf_no = Column(String(45), nullable=True)
    esi_no = Column(String(45), nullable=True)
    id_type = Column(String(255), nullable=True)
    id_number = Column(String(45), nullable=True)
    ref_check = Column(String(255), nullable=True)
    disbursement_target = Column(Numeric(10, 2), nullable=True)
    collection_target = Column(Numeric(10, 2), nullable=True)
    onboarding_target = Column(String(45), nullable=True)
    status = Column(String(2), nullable=True)
    del_mark = Column(String(2), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
