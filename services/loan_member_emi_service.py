from cProfile import label
from sqlalchemy.orm import Session
from models.loan_member_emi import LoanMemberEmi
from models.loan import Loan
from models.loan_member import LoanMember
from schemas.loan_member_emi import LoanMemberEmiCreate
from datetime import datetime, timedelta
from decimal import Decimal
import math
import logging

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LoanMemberEmiService:
    @staticmethod
    def generate_emi_schedule(db: Session, loan_id: int, created_by: str) -> list:
        """Generate EMI schedule for all members of a loan"""
        logger.info(f"Starting EMI schedule generation for loan_id: {loan_id}")
        try:
            loan = db.query(Loan).filter(Loan.id == loan_id).first()
            if not loan:
                logger.error(f"Loan not found: {loan_id}")
                return []

            logger.debug(f"Loan found: {loan.loan_id} - Amount: {loan.loan_amount}, Rate: {loan.interest_rate}%, Tenure: {loan.loan_tenure}")

            loan_members = db.query(LoanMember).filter(LoanMember.loan_id == loan_id).all()
            if not loan_members:
                logger.error(f"No loan members found for loan_id: {loan_id}")
                return []

            logger.info(f"Found {len(loan_members)} loan members for loan_id: {loan_id}")
            emi_records = []

            # Calculate EMI details
            principal_amount = float(loan.loan_amount)
            interest_amount = float(loan.interest_amount) if loan.interest_amount else 0
            num_installments = int(loan.loan_tenure) if loan.loan_tenure else 12
            
            # Calculate EMI: (Principal + Interest Amount) / Number of Installments
            total_amount = principal_amount + interest_amount
            emi_amount = total_amount / num_installments

            logger.info(f"EMI Calculation - Principal: ₹{principal_amount}, Interest Amount: ₹{interest_amount}, Tenure: {num_installments} installments, EMI: ₹{round(emi_amount, 2)}")

            repayment_freq = loan.repayment_frequency or 'month'

            weekly_first_emi_date = None
            if repayment_freq == 'week':
                weekday_map = {
                    'monday': 0,
                    'tuesday': 1,
                    'wednesday': 2,
                    'thursday': 3,
                    'friday': 4,
                    'saturday': 5,
                    'sunday': 6,
                }

                raw_emi_day = (loan.emi_day or '').strip().lower()
                target_weekday = weekday_map.get(raw_emi_day)
                base_date = loan.loan_start_date or datetime.utcnow().date()

                if target_weekday is not None:
                    days_ahead = (target_weekday - base_date.weekday()) % 7
                    weekly_first_emi_date = base_date + timedelta(days=days_ahead)
                else:
                    weekly_first_emi_date = base_date

            # Generate EMI schedule for each loan member
            for member_idx, loan_member in enumerate(loan_members, 1):
                logger.debug(f"Processing loan member {member_idx}/{len(loan_members)} - Member ID: {loan_member.member_id}")
                start_date = loan.loan_start_date if loan.loan_start_date else datetime.utcnow()
                
                for emi_num in range(1, num_installments + 1):
                    # Calculate EMI date based on repayment frequency
                    if repayment_freq == 'month':
                        emi_date = start_date + timedelta(days=30 * emi_num)
                    elif repayment_freq == 'week':
                        first = weekly_first_emi_date or (loan.loan_start_date or datetime.utcnow().date())
                        emi_date = datetime.combine(first, datetime.min.time()) + timedelta(weeks=emi_num - 1)
                    else:  # quarterly or other
                        emi_date = start_date + timedelta(days=90 * emi_num)

                    # Calculate principal and interest for this EMI
                    # remaining_principal = principal_amount
                    # for i in range(1, emi_num):
                    #     interest = remaining_principal * monthly_rate
                    #     principal = emi_amount - interest
                    #     remaining_principal -= principal

                    # interest_amount = remaining_principal * monthly_rate
                    # principal_for_emi = emi_amount - interest_amount

                    # Create EMI record for this member
                    emi_record = LoanMemberEmi(
                        loan_id=loan_id,
                        member_id=loan_member.member_id,
                        emi_date=emi_date,
                        emi_amount=Decimal(str(round(emi_amount, 2))),
                        emi_delay='0',
                        emi_status='PENDING',
                        label='UPCOMING',
                        created_by=created_by,
                    )
                    db.add(emi_record)
                    emi_records.append(emi_record)
                
                logger.debug(f"Created {num_installments} EMI records for member {loan_member.member_id}")

            # Commit all records
            db.commit()
            logger.info(f"Successfully committed {len(emi_records)} EMI records to database")
            
            for record in emi_records:
                db.refresh(record)

            logger.info(f"EMI schedule generation completed successfully for loan_id: {loan_id}")
            return emi_records
        
        except Exception as e:
            logger.exception(f"Error generating EMI schedule for loan_id: {loan_id} - Error: {str(e)}")
            db.rollback()
            return []

    @staticmethod
    def get_emi_schedule_for_loan(db: Session, loan_id: int) -> list:
        """Get EMI schedule for a specific loan"""
        return db.query(LoanMemberEmi).filter(LoanMemberEmi.loan_id == loan_id).order_by(
            LoanMemberEmi.member_id, LoanMemberEmi.id).all()

    @staticmethod
    def get_emi_schedule_for_member(db: Session, loan_member_id: int) -> list:
        """Get EMI schedule for a specific loan member"""
        return db.query(LoanMemberEmi).filter(LoanMemberEmi.member_id == loan_member_id).order_by(
            LoanMemberEmi.emi_number
        ).all()

    @staticmethod
    def update_emi_collection(db: Session, emi_id: int, collected_amount: Decimal, updated_by: str) -> LoanMemberEmi:
        """Update collected amount for an EMI"""
        emi = db.query(LoanMemberEmi).filter(LoanMemberEmi.id == emi_id).first()
        
        if emi:
            emi.collected_amount = collected_amount
            emi.pending_amount = emi.emi_amount - collected_amount
            
            # Update status based on collection
            if collected_amount >= emi.emi_amount:
                emi.emi_status = 'Collected'
            elif collected_amount > 0:
                emi.emi_status = 'Partial'
            else:
                emi.emi_status = 'Pending'
            
            emi.updated_by = updated_by
            emi.updated_at = datetime.now()
            
            db.commit()
            db.refresh(emi)
        
        return emi

    @staticmethod
    def delete_emi_schedule(db: Session, loan_id: int) -> int:
        """Delete EMI schedule for a loan"""
        count = db.query(LoanMemberEmi).filter(LoanMemberEmi.loan_id == loan_id).delete()
        db.commit()
        return count
