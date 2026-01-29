from sqlalchemy.orm import Session
from models.loan import Loan
from models.loan_member import LoanMember
from models.loan_member_emi import LoanMemberEmi
from models.member_group import MemberGroup
from services.billing_service import BillingService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CollectionService:
    @staticmethod
    def get_collection_list(db: Session, skip: int = 0, limit: int = 100) -> list:
        """
        Get collection list with approved loans only.
        Combines loans, loan_members, and loan_member_emi data.
        """
        logger.info("Fetching collection list for approved loans")
        try:
            # Fetch only approved loans
            approved_loans = db.query(Loan).filter(
                Loan.loan_status == 'Approved',
                Loan.del_mark != 'Y'
            ).order_by(Loan.id.desc()).offset(skip).limit(limit).all()

            logger.info(f"Found {len(approved_loans)} approved loans")

            collection_list = []

            for loan in approved_loans:
                # Get loan members for this loan
                loan_members = db.query(LoanMember).filter(
                    LoanMember.loan_id == loan.id
                ).all()

                logger.debug(f"Loan {loan.loan_id}: Found {len(loan_members)} members")

                # Get member group name
                group_name = ''
                if loan.member_group_id:
                    member_group = db.query(MemberGroup).filter(
                        MemberGroup.id == loan.member_group_id
                    ).first()
                    if member_group:
                        group_name = member_group.name

                # Get EMI schedule for this loan
                emi_schedule = db.query(LoanMemberEmi).filter(
                    LoanMemberEmi.loan_id == loan.id
                ).order_by(LoanMemberEmi.emi_date).all()

                logger.debug(f"Loan {loan.loan_id}: Found {len(emi_schedule)} EMI records")

                # Calculate totals from loan_members table
                total_collected = sum(float(member.collected or 0) for member in loan_members)
                total_pending = sum(float(member.pending or 0) for member in loan_members)
                
                logger.debug(f"Loan {loan.loan_id}: Total Collected: {total_collected}, Total Pending: {total_pending}")

                # Build members array with EMI data
                members = []
                for loan_member in loan_members:
                    # Get EMI records for this member
                    member_emis = [emi for emi in emi_schedule if emi.member_id == loan_member.member_id]
                    
                    # Calculate member totals from loan_members table
                    member_collected = float(loan_member.collected or 0)
                    member_pending = float(loan_member.pending or 0)
                    member_total = member_collected + member_pending

                    members.append({
                        'id': loan_member.member_id,
                        'name': loan_member.name,
                        'place': loan_member.place,
                        'phone': loan_member.phone,
                        'collectedAmount': member_collected,
                        'pendingAmount': member_pending,
                        'totalAmount': member_total,
                        'emiSchedule': [
                            {
                                'id': emi.id,
                                'dueDate': emi.emi_date.isoformat() if emi.emi_date else None,
                                'amount': float(emi.emi_amount or 0),
                                'status': emi.emi_status if hasattr(emi, 'emi_status') else 'Pending',
                                'label': emi.label if hasattr(emi, 'label') else 'UPCOMING',
                            }
                            for emi in member_emis
                        ]
                    })

                # Determine collection status based on EMI status
                collection_status = 'Active'
                if total_pending == 0:
                    collection_status = 'Completed'
                elif any(emi.emi_status == 'Overdue' if hasattr(emi, 'emi_status') else False for emi in emi_schedule):
                    collection_status = 'Overdue'

                # Build collection object
                collection = {
                    'id': loan.id,
                    'loanId': loan.loan_id,
                    'groupName': group_name,
                    'memberGroupId': loan.member_group_id,
                    'members': members,
                    'loanAmount': float(loan.loan_amount* len(loan_members) or 0),
                    'collectedAmount': total_collected,
                    'pendingAmount': total_pending,
                    'frequency': loan.repayment_frequency or 'month',
                    'emiDay': loan.emi_day or 'N/A',
                    'assign_to': loan.assign_to or None,
                    'createdDate': loan.created_at.isoformat() if loan.created_at else None,
                    'status': collection_status,
                    'nextDueDate': emi_schedule[0].emi_date.isoformat() if emi_schedule and emi_schedule[0].emi_date else None,
                    'loanStartDate': loan.loan_start_date.isoformat() if loan.loan_start_date else None,
                    'interestRate': float(loan.interest_rate or 0),
                    'loanTenure': loan.loan_tenure,
                    'monthlyEmi': float(loan.monthly_emi or 0),
                }

                collection_list.append(collection)

            logger.info(f"Successfully built collection list with {len(collection_list)} items")
            return collection_list

        except Exception as e:
            logger.exception(f"Error fetching collection list: {str(e)}")
            return []

    @staticmethod
    def get_collection_by_loan_id(db: Session, loan_id: int) -> dict:
        """Get collection details for a specific loan"""
        logger.info(f"Fetching collection details for loan_id: {loan_id}")
        try:
            loan = db.query(Loan).filter(Loan.id == loan_id).first()
            if not loan:
                logger.error(f"Loan not found: {loan_id}")
                return {}

            # Get member group name
            group_name = ''
            if loan.member_group_id:
                member_group = db.query(MemberGroup).filter(
                    MemberGroup.id == loan.member_group_id
                ).first()
                if member_group:
                    group_name = member_group.name

            loan_members = db.query(LoanMember).filter(LoanMember.loan_id == loan_id).all()
            emi_schedule = db.query(LoanMemberEmi).filter(LoanMemberEmi.loan_id == loan_id).order_by(
                LoanMemberEmi.emi_date
            ).all()

            # Calculate totals from loan_members table
            total_collected = sum(float(member.collected or 0) for member in loan_members)
            total_pending = sum(float(member.pending or 0) for member in loan_members)

            members = []
            for loan_member in loan_members:
                member_emis = [emi for emi in emi_schedule if emi.member_id == loan_member.id]
                
                # Get member totals from loan_members table
                member_collected = float(loan_member.collected or 0)
                member_pending = float(loan_member.pending or 0)
                member_total = member_collected + member_pending

                members.append({
                    'id': loan_member.id,
                    'name': loan_member.name,
                    'place': loan_member.place,
                    'phone': loan_member.phone,
                    'collectedAmount': member_collected,
                    'pendingAmount': member_pending,
                    'totalAmount': member_total,
                    'emiSchedule': [
                        {
                            'id': emi.id,
                            'dueDate': emi.emi_date.isoformat() if emi.emi_date else None,
                            'amount': float(emi.emi_amount or 0),
                            'status': emi.emi_status if hasattr(emi, 'emi_status') else 'Pending',
                            'label': emi.label if hasattr(emi, 'label') else 'UPCOMING',
                        }
                        for emi in member_emis
                    ]
                })

            collection_status = 'Active'
            if total_pending == 0:
                collection_status = 'Completed'
            elif any(emi.emi_status == 'Overdue' if hasattr(emi, 'emi_status') else False for emi in emi_schedule):
                collection_status = 'Overdue'

            collection = {
                'id': loan.id,
                'loanId': loan.loan_id,
                'groupName': group_name,
                'memberGroupId': loan.member_group_id,
                'members': members,
                'loanAmount': float(loan.loan_amount or 0),
                'collectedAmount': total_collected,
                'pendingAmount': total_pending,
                'frequency': loan.repayment_frequency or 'month',
                'emiDay': loan.emi_day or 'N/A',
                'assign_to': loan.assign_to or None,
                'createdDate': loan.created_at.isoformat() if loan.created_at else None,
                'status': collection_status,
                'nextDueDate': emi_schedule[0].emi_date.isoformat() if emi_schedule and emi_schedule[0].emi_date else None,
                'loanStartDate': loan.loan_start_date.isoformat() if loan.loan_start_date else None,
                'interestRate': float(loan.interest_rate or 0),
                'loanTenure': loan.loan_tenure,
                'monthlyEmi': float(loan.monthly_emi or 0),
            }

            logger.info(f"Successfully fetched collection details for loan_id: {loan_id}")
            return collection

        except Exception as e:
            logger.exception(f"Error fetching collection details: {str(e)}")
            return {}

    @staticmethod
    def process_emi_payment(db: Session, emi_id: int, amount: float, paid_by: str = "System") -> dict:
        """Process EMI payment and update status"""
        logger.info(f"Processing payment for EMI ID: {emi_id}, Amount: {amount}")
        try:
            # Get the EMI record
            emi = db.query(LoanMemberEmi).filter(LoanMemberEmi.id == emi_id).first()
            if not emi:
                logger.error(f"EMI not found: {emi_id}")
                return {}

            # Update EMI status and label
            emi.emi_status = 'PAID'
            emi.label = 'PAID'
            emi.updated_at = datetime.now()

            # Get the loan member to update collected and pending amounts
            loan_member = db.query(LoanMember).filter(LoanMember.loan_id == emi.loan_id , LoanMember.member_id == emi.member_id).first()
            if loan_member:
                # Update collected and pending amounts
                loan_member.collected = float(loan_member.collected or 0) + float(amount)
                loan_member.pending = float(loan_member.pending or 0) - float(amount)
                if loan_member.pending < 0:
                    loan_member.pending = 0
                logger.debug(f"Updated loan member {loan_member.id}: collected={loan_member.collected}, pending={loan_member.pending}")

                # Create billing entry for payment (CREDIT)
                BillingService.create_payment_billing(
                    db=db,
                    loan_id=emi.loan_id,
                    member_id=emi.member_id,
                    member_group_id=loan_member.member_group_id,
                    amount=amount,
                    created_by=paid_by
                )

            db.commit()
            db.refresh(emi)

            logger.info(f"Successfully processed payment for EMI ID: {emi_id}")
            return {
                'id': emi.id,
                'emi_status': emi.emi_status,
                'label': emi.label,
                'member_collected': float(loan_member.collected or 0) if loan_member else 0,
                'member_pending': float(loan_member.pending or 0) if loan_member else 0,
            }

        except Exception as e:
            logger.exception(f"Error processing EMI payment: {str(e)}")
            db.rollback()
            return {}
