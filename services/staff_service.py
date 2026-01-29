from sqlalchemy.orm import Session
from models.staff import Staff
from schemas.staff_schema import StaffCreate, StaffUpdate
from datetime import datetime


class StaffService:
    @staticmethod
    def create_staff(db: Session, staff: StaffCreate) -> Staff:
        """Create a new staff member"""
        db_staff = Staff(
            staff_id=staff.staff_id,
            name=staff.name,
            email=staff.email,
            phone=staff.phone,
            dob=staff.dob,
            gender=staff.gender,
            p_address=staff.p_address,
            doj=staff.doj,
            designation=staff.designation,
            reporting_to=staff.reporting_to,
            branch=staff.branch,
            staff_status=staff.staff_status,
            department=staff.department,
            bank_ac=staff.bank_ac,
            bank_ifsc=staff.bank_ifsc,
            ac_holder_name=staff.ac_holder_name,
            salary=staff.salary,
            epf_no=staff.epf_no,
            esi_no=staff.esi_no,
            id_type=staff.id_type,
            id_number=staff.id_number,
            ref_check=staff.ref_check,
            disbursement_target=staff.disbursement_target,
            collection_target=staff.collection_target,
            onboarding_target=staff.onboarding_target,
            status='A',
            del_mark='N',
            created_at=datetime.now(),
            created_by='Admin',
        )
        db.add(db_staff)
        db.commit()
        db.refresh(db_staff)
        return db_staff

    @staticmethod
    def get_staff(db: Session, staff_id: int) -> Staff:
        """Get a staff member by ID"""
        return db.query(Staff).filter(Staff.id == staff_id, Staff.del_mark == 'N').first()

    @staticmethod
    def get_all_staff(db: Session, skip: int = 0, limit: int = 100) -> list:
        """Get all active staff members"""
        return db.query(Staff).filter(
            Staff.del_mark == 'N'
        ).order_by(Staff.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_staff_by_email(db: Session, email: str) -> Staff:
        """Get staff member by email"""
        return db.query(Staff).filter(Staff.email == email, Staff.del_mark == 'N').first()

    @staticmethod
    def update_staff(db: Session, staff_id: int, staff: StaffUpdate) -> Staff:
        """Update a staff member"""
        db_staff = StaffService.get_staff(db, staff_id)
        if not db_staff:
            return None

        if staff.name is not None:
            db_staff.name = staff.name
        if staff.email is not None:
            db_staff.email = staff.email
        if staff.phone is not None:
            db_staff.phone = staff.phone
        if staff.dob is not None:
            db_staff.dob = staff.dob
        if staff.gender is not None:
            db_staff.gender = staff.gender
        if staff.p_address is not None:
            db_staff.p_address = staff.p_address
        if staff.doj is not None:
            db_staff.doj = staff.doj
        if staff.designation is not None:
            db_staff.designation = staff.designation
        if staff.reporting_to is not None:
            db_staff.reporting_to = staff.reporting_to
        if staff.branch is not None:
            db_staff.branch = staff.branch
        if staff.staff_status is not None:
            db_staff.staff_status = staff.staff_status
        if staff.department is not None:
            db_staff.department = staff.department
        if staff.bank_ac is not None:
            db_staff.bank_ac = staff.bank_ac
        if staff.bank_ifsc is not None:
            db_staff.bank_ifsc = staff.bank_ifsc
        if staff.ac_holder_name is not None:
            db_staff.ac_holder_name = staff.ac_holder_name
        if staff.salary is not None:
            db_staff.salary = staff.salary
        if staff.epf_no is not None:
            db_staff.epf_no = staff.epf_no
        if staff.esi_no is not None:
            db_staff.esi_no = staff.esi_no
        if staff.id_type is not None:
            db_staff.id_type = staff.id_type
        if staff.id_number is not None:
            db_staff.id_number = staff.id_number
        if staff.ref_check is not None:
            db_staff.ref_check = staff.ref_check
        if staff.disbursement_target is not None:
            db_staff.disbursement_target = staff.disbursement_target
        if staff.collection_target is not None:
            db_staff.collection_target = staff.collection_target
        if staff.onboarding_target is not None:
            db_staff.onboarding_target = staff.onboarding_target
        if staff.updated_by is not None:
            db_staff.updated_by = staff.updated_by

        db_staff.updated_at = datetime.now()
        db.add(db_staff)
        db.commit()
        db.refresh(db_staff)
        return db_staff

    @staticmethod
    def delete_staff(db: Session, staff_id: int, deleted_by: str) -> Staff:
        """Soft delete a staff member"""
        db_staff = StaffService.get_staff(db, staff_id)
        if not db_staff:
            return None

        db_staff.del_mark = 'Y'
        db_staff.status = 'I'
        db_staff.updated_by = deleted_by
        db_staff.updated_at = datetime.now()

        db.add(db_staff)
        db.commit()
        db.refresh(db_staff)
        return db_staff

    @staticmethod
    def search_staff(db: Session, query: str, skip: int = 0, limit: int = 100) -> list:
        """Search staff by name, email, or staff_id"""
        return db.query(Staff).filter(
            Staff.del_mark == 'N',
            (
                Staff.name.ilike(f'%{query}%') |
                Staff.email.ilike(f'%{query}%') |
                Staff.staff_id.ilike(f'%{query}%')
            )
        ).offset(skip).limit(limit).all()
