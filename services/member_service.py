from sqlalchemy.orm import Session
from models.member import Member
from schemas.member import MemberCreate, MemberUpdate
from datetime import datetime


class MemberService:
    @staticmethod
    def create_member(db: Session, member: MemberCreate) -> Member:
        """Create a new member"""
        db_member = Member(
            full_name=member.full_name,
            father_spouse_name=member.father_spouse_name,
            date_of_birth=member.date_of_birth,
            gender=member.gender,
            marital_status=member.marital_status,
            place=member.place,
            adhar_number=member.adhar_number,
            pan_number=member.pan_number,
            customer_photo=member.customer_photo,
            primary_mobile_number=member.primary_mobile_number,
            alternate_contact_number=member.alternate_contact_number,
            email_address=member.email_address,
            current_address=member.current_address,
            pincode=member.pincode,
            residence_type=member.residence_type,
            years_at_current_residence=member.years_at_current_residence,
            permanent_address=member.permanent_address,
            occupation_type=member.occupation_type,
            employer_business_name=member.employer_business_name,
            work_address=member.work_address,
            designation=member.designation,
            monthly_gross_income=member.monthly_gross_income,
            monthly_net_income=member.monthly_net_income,
            total_work_experience=member.total_work_experience,
            existing_active_loans=member.existing_active_loans,
            total_monthly_emi=member.total_monthly_emi,
            number_of_dependents=member.number_of_dependents,
            account_holder_name=member.account_holder_name,
            bank_name=member.bank_name,
            account_number=member.account_number,
            ifsc_code=member.ifsc_code,
            branch_name=member.branch_name,
            guarantor_name=member.guarantor_name,
            guarantor_relationship=member.guarantor_relationship,
            guarantor_contact_number=member.guarantor_contact_number,
            guarantor_kyc_id=member.guarantor_kyc_id,
            status='A',
            del_mark='N',
            created_by=member.created_by,
        )
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def get_member(db: Session, member_id: int) -> Member:
        """Get a member by ID"""
        return db.query(Member).filter(
            Member.id == member_id,
            Member.del_mark == 'N'
        ).first()

    @staticmethod
    def get_members(db: Session, skip: int = 0, limit: int = 100) -> list:
        """Get all active members"""
        return db.query(Member).filter(
            Member.del_mark == 'N'
        ).order_by(Member.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_member_by_mobile(db: Session, mobile_number: str) -> Member:
        """Get a member by mobile number"""
        return db.query(Member).filter(
            Member.primary_mobile_number == mobile_number,
            Member.del_mark == 'N'
        ).first()

    @staticmethod
    def update_member(db: Session, member_id: int, member_update: MemberUpdate) -> Member:
        """Update a member"""
        db_member = MemberService.get_member(db, member_id)
        if not db_member:
            return None

        update_data = member_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(db_member, field, value)

        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def delete_member(db: Session, member_id: int, deleted_by: str) -> Member:
        """Soft delete a member (set del_mark='Y' and status='I')"""
        db_member = MemberService.get_member(db, member_id)
        if not db_member:
            return None

        db_member.del_mark = 'Y'
        db_member.status = 'I'
        db_member.updated_by = deleted_by
        db_member.updated_at = datetime.utcnow()

        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def reactivate_member(db: Session, member_id: int, reactivated_by: str) -> Member:
        """Reactivate a deleted member (set del_mark='N' and status='A')"""
        db_member = db.query(Member).filter(Member.id == member_id).first()
        if not db_member:
            return None

        db_member.del_mark = 'N'
        db_member.status = 'A'
        db_member.updated_by = reactivated_by
        db_member.updated_at = datetime.utcnow()

        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def get_members_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> list:
        """Get members by status"""
        return db.query(Member).filter(
            Member.status == status,
            Member.del_mark == 'N'
        ).offset(skip).limit(limit).all()

    @staticmethod
    def search_members(db: Session, search_query: str, skip: int = 0, limit: int = 100) -> list:
        """Search members by name or mobile number"""
        return db.query(Member).filter(
            (Member.full_name.ilike(f"%{search_query}%") |
             Member.primary_mobile_number.ilike(f"%{search_query}%")),
            Member.del_mark == 'N'
        ).offset(skip).limit(limit).all()
