from sqlalchemy.orm import Session
from models.loan import Loan
from schemas.loan import LoanCreate, LoanUpdate
from services.loan_member_service import LoanMemberService
from services.loan_member_emi_service import LoanMemberEmiService
from services.billing_service import BillingService
from datetime import datetime


class LoanService:
    @staticmethod
    def create_loan(db: Session, loan: LoanCreate) -> Loan:
        """Create a new loan"""
        db_loan = Loan(
            loan_id=loan.loan_id,
            member_group_id=loan.member_group_id,
            application_date=loan.application_date,
            loan_amount=loan.loan_amount,
            loan_type=loan.loan_type,
            interest_rate=loan.interest_rate,
            interest_amount=loan.interest_amount,
            loan_tenure=loan.loan_tenure,
            monthly_emi=loan.monthly_emi,
            emi_day=loan.emi_day,
            loan_start_date=loan.loan_start_date,
            repayment_frequency=loan.repayment_frequency,
            processing_fees=loan.processing_fees,
            insurance_fees=loan.insurance_fees,
            other_fees=loan.other_fees,
            field_officer_id=loan.field_officer_id,
            visit_date=loan.visit_date,
            geo_tagging=loan.geo_tagging,
            business_asset_verification=loan.business_asset_verification,
            cash_flow_analysis=loan.cash_flow_analysis,
            credit_officer_comments=loan.credit_officer_comments,
            verification_status=loan.verification_status,
            loan_status=loan.loan_status or 'Draft',
            status='A',
            del_mark='N',
            created_by=loan.created_by,
        )
        db.add(db_loan)
        db.commit()
        db.refresh(db_loan)
        
        if loan.member_group_id:
            LoanMemberService.create_loan_members_for_group(
                db,
                db_loan.id,
                loan.member_group_id,
                loan.loan_amount,
                loan.created_by
            )
        
        return db_loan

    @staticmethod
    def get_loan(db: Session, loan_id: int) -> Loan:
        """Get a loan by ID"""
        return db.query(Loan).filter(Loan.id == loan_id, Loan.del_mark == 'N').first()

    @staticmethod
    def get_loans(db: Session, skip: int = 0, limit: int = 100) -> list:
        """Get all active loans"""
        return db.query(Loan).filter(
            Loan.del_mark == 'N'
        ).order_by(Loan.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_loans_by_member(db: Session, member_id: int, skip: int = 0, limit: int = 100) -> list:
        """Get all loans for a specific member (via member group)"""
        return db.query(Loan).filter(
            Loan.del_mark == 'N'
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_loans_by_group(db: Session, group_id: int, skip: int = 0, limit: int = 100) -> list:
        """Get all loans for a specific member group"""
        return db.query(Loan).filter(
            Loan.member_group_id == group_id,
            Loan.del_mark == 'N'
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update_loan(db: Session, loan_id: int, loan: LoanUpdate) -> Loan:
        """Update a loan"""
        db_loan = LoanService.get_loan(db, loan_id)
        if not db_loan:
            return None

        if loan.loan_id is not None:
            db_loan.loan_id = loan.loan_id
        if loan.member_group_id is not None:
            db_loan.member_group_id = loan.member_group_id
        if loan.application_date is not None:
            db_loan.application_date = loan.application_date
        if loan.loan_amount is not None:
            db_loan.loan_amount = loan.loan_amount
            # Sync loan amount to all loan members
            LoanMemberService.update_loan_members_amount(db, loan_id, loan.loan_amount)
        if loan.loan_type is not None:
            db_loan.loan_type = loan.loan_type
        if loan.interest_rate is not None:
            db_loan.interest_rate = loan.interest_rate
        if loan.interest_amount is not None:
            db_loan.interest_amount = loan.interest_amount
        if loan.loan_tenure is not None:
            db_loan.loan_tenure = loan.loan_tenure
        if loan.monthly_emi is not None:
            db_loan.monthly_emi = loan.monthly_emi
        if loan.emi_day is not None:
            db_loan.emi_day = loan.emi_day
        if loan.loan_start_date is not None:
            db_loan.loan_start_date = loan.loan_start_date
        if loan.repayment_frequency is not None:
            db_loan.repayment_frequency = loan.repayment_frequency
        if loan.processing_fees is not None:
            db_loan.processing_fees = loan.processing_fees
        if loan.insurance_fees is not None:
            db_loan.insurance_fees = loan.insurance_fees
        if loan.other_fees is not None:
            db_loan.other_fees = loan.other_fees
        if loan.field_officer_id is not None:
            db_loan.field_officer_id = loan.field_officer_id
        if loan.visit_date is not None:
            db_loan.visit_date = loan.visit_date
        if loan.geo_tagging is not None:
            db_loan.geo_tagging = loan.geo_tagging
        if loan.business_asset_verification is not None:
            db_loan.business_asset_verification = loan.business_asset_verification
        if loan.cash_flow_analysis is not None:
            db_loan.cash_flow_analysis = loan.cash_flow_analysis
        if loan.credit_officer_comments is not None:
            db_loan.credit_officer_comments = loan.credit_officer_comments
        if loan.verification_status is not None:
            db_loan.verification_status = loan.verification_status
        if loan.loan_status is not None:
            old_status = db_loan.loan_status
            db_loan.loan_status = loan.loan_status
            
            # Generate EMI schedule and create billing entries when status changes to 'Approved'
            if loan.loan_status == 'Approved' and old_status != 'Approved':
                updated_by = loan.updated_by or 'system'
                LoanMemberEmiService.generate_emi_schedule(db, loan_id, updated_by)
                # Create billing entries for loan approval
                BillingService.create_loan_approval_billing(db, loan_id, updated_by)
        
        if loan.assign_to is not None:
            db_loan.assign_to = loan.assign_to
        
        if loan.updated_by is not None:
            db_loan.updated_by = loan.updated_by
        
        db_loan.updated_at = datetime.utcnow()
        db.add(db_loan)
        db.commit()
        db.refresh(db_loan)
        return db_loan

    @staticmethod
    def delete_loan(db: Session, loan_id: int, deleted_by: str) -> Loan:
        """Soft delete a loan (set del_mark='Y' and status='I')"""
        db_loan = LoanService.get_loan(db, loan_id)
        if not db_loan:
            return None

        db_loan.del_mark = 'Y'
        db_loan.status = 'I'
        db_loan.updated_by = deleted_by
        db_loan.updated_at = datetime.utcnow()

        db.add(db_loan)
        db.commit()
        db.refresh(db_loan)
        return db_loan

    @staticmethod
    def reactivate_loan(db: Session, loan_id: int, reactivated_by: str) -> Loan:
        """Reactivate a soft-deleted loan"""
        db_loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not db_loan:
            return None

        db_loan.del_mark = 'N'
        db_loan.status = 'A'
        db_loan.updated_by = reactivated_by
        db_loan.updated_at = datetime.utcnow()

        db.add(db_loan)
        db.commit()
        db.refresh(db_loan)
        return db_loan

    @staticmethod
    def search_loans(db: Session, query: str, skip: int = 0, limit: int = 100) -> list:
        """Search loans by loan_id or member details"""
        return db.query(Loan).filter(
            Loan.del_mark == 'N',
            (Loan.loan_id.ilike(f'%{query}%'))
        ).offset(skip).limit(limit).all()
