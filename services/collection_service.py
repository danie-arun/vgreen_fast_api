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
    def get_collection_list(db: Session, org: str = None, skip: int = 0, limit: int = 100) -> list:
        """
        Get collection list with approved loans only for authenticated user's org.
        Combines loans, loan_members, and loan_member_emi data.
        """
        logger.info(f"Fetching collection list for approved loans in org: {org}")
        try:
            # Fetch only approved loans for the user's org
            query = db.query(Loan).filter(
                Loan.loan_status == 'Approved',
                Loan.del_mark != 'Y'
            )
            
            if org:
                query = query.filter(Loan.org == org)
            
            approved_loans = query.order_by(Loan.id.desc()).offset(skip).limit(limit).all()

            if not approved_loans:
                return []

            loan_ids = [loan.id for loan in approved_loans]
            
            # Batch fetch all related data
            loan_members_all = db.query(LoanMember).filter(
                LoanMember.loan_id.in_(loan_ids)
            ).all()
            
            groups_all = db.query(MemberGroup).filter(
                MemberGroup.id.in_([l.member_group_id for l in approved_loans if l.member_group_id])
            ).all()
            
            emi_schedule_all = db.query(LoanMemberEmi).filter(
                LoanMemberEmi.loan_id.in_(loan_ids)
            ).order_by(LoanMemberEmi.emi_date).all()
            
            # Create lookup dictionaries for O(1) access
            members_by_loan = {}
            for member in loan_members_all:
                if member.loan_id not in members_by_loan:
                    members_by_loan[member.loan_id] = []
                members_by_loan[member.loan_id].append(member)
            
            groups_by_id = {g.id: g for g in groups_all}
            
            emi_by_loan = {}
            for emi in emi_schedule_all:
                if emi.loan_id not in emi_by_loan:
                    emi_by_loan[emi.loan_id] = []
                emi_by_loan[emi.loan_id].append(emi)
            
            emi_by_member = {}
            for emi in emi_schedule_all:
                key = (emi.loan_id, emi.member_id)
                if key not in emi_by_member:
                    emi_by_member[key] = []
                emi_by_member[key].append(emi)

            collection_list = []

            for loan in approved_loans:
                # Get data from lookup dictionaries
                loan_members = members_by_loan.get(loan.id, [])
                group = groups_by_id.get(loan.member_group_id)
                emi_schedule = emi_by_loan.get(loan.id, [])
                
                group_name = group.name if group else ''

                # Calculate totals from loan_members table
                total_collected = sum(float(member.collected or 0) for member in loan_members)
                total_pending = sum(float(member.pending or 0) for member in loan_members)
                total_principal = sum(float(member.amount or 0) for member in loan_members)
                per_member_interest = float(getattr(loan, 'interest_amount', 0) or 0)
                total_interest = per_member_interest * len(loan_members)
                
                logger.debug(f"Loan {loan.loan_id}: Total Collected: {total_collected}, Total Pending: {total_pending}")

                # Build members array with EMI data
                members = []
                for loan_member in loan_members:
                    # Get EMI records for this member from lookup
                    member_emis = emi_by_member.get((loan.id, loan_member.member_id), [])
                    
                    # Calculate member totals from loan_members table
                    member_collected = float(loan_member.collected or 0)
                    member_pending = float(loan_member.pending or 0)
                    member_pending_with_interest = member_pending + per_member_interest
                    member_total = member_collected + member_pending_with_interest

                    members.append({
                        'id': loan_member.member_id,
                        'name': loan_member.name,
                        'place': loan_member.place,
                        'phone': loan_member.phone,
                        'collectedAmount': member_collected,
                        'pendingAmount': member_pending_with_interest,
                        'advanceAmount': float(getattr(loan_member, 'advance', 0) or 0),
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
                    'loanAmount': float(total_principal + total_interest),
                    'collectedAmount': total_collected,
                    'pendingAmount': float(total_pending + total_interest),
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
    def get_collection_by_loan_id(db: Session, loan_id: int, org: str = None) -> dict:
        """Get collection details for a specific loan for authenticated user's org"""
        logger.info(f"Fetching collection details for loan_id: {loan_id} in org: {org}")
        try:
            query = db.query(Loan).filter(Loan.id == loan_id)
            if org:
                query = query.filter(Loan.org == org)
            
            loan = query.first()
            if not loan:
                logger.error(f"Loan not found: {loan_id}")
                return {}

            # Batch fetch all related data
            loan_members = db.query(LoanMember).filter(LoanMember.loan_id == loan_id).all()
            emi_schedule = db.query(LoanMemberEmi).filter(LoanMemberEmi.loan_id == loan_id).order_by(
                LoanMemberEmi.emi_date
            ).all()
            
            # Get member group name with single query
            group_name = ''
            if loan.member_group_id:
                member_group = db.query(MemberGroup).filter(
                    MemberGroup.id == loan.member_group_id
                ).first()
                if member_group:
                    group_name = member_group.name
            
            # Create lookup dictionary for EMI by member
            emi_by_member = {}
            for emi in emi_schedule:
                key = emi.member_id
                if key not in emi_by_member:
                    emi_by_member[key] = []
                emi_by_member[key].append(emi)

            # Calculate totals from loan_members table
            total_collected = sum(float(member.collected or 0) for member in loan_members)
            total_pending = sum(float(member.pending or 0) for member in loan_members)
            total_principal = sum(float(member.amount or 0) for member in loan_members)
            per_member_interest = float(getattr(loan, 'interest_amount', 0) or 0)
            total_interest = per_member_interest * len(loan_members)

            members = []
            for loan_member in loan_members:
                # Get EMI records for this member from lookup
                member_emis = emi_by_member.get(loan_member.member_id, [])
                
                # Get member totals from loan_members table
                member_collected = float(loan_member.collected or 0)
                member_pending = float(loan_member.pending or 0)
                member_pending_with_interest = member_pending + per_member_interest
                member_total = member_collected + member_pending_with_interest

                members.append({
                    'id': loan_member.member_id,
                    'name': loan_member.name,
                    'place': loan_member.place,
                    'phone': loan_member.phone,
                    'collectedAmount': member_collected,
                    'pendingAmount': member_pending_with_interest,
                    'advanceAmount': float(getattr(loan_member, 'advance', 0) or 0),
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
                'loanAmount': float(total_principal + total_interest),
                'collectedAmount': total_collected,
                'pendingAmount': float(total_pending + total_interest),
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
    def process_emi_payment(
        db: Session,
        emi_id: int,
        amount: float,
        paid_by: str = "System",
        org: str = None,
        loan_advance: float = 0,
        credit_officer: str = "",
    ) -> dict:
        """Process EMI payment and update status for authenticated user's org"""
        print(f"Processing payment for EMI ID: {emi_id}, Amount: {amount}, Org: {org}")
        try:
            if not (credit_officer or "").strip():
                raise ValueError("Credit Officer is required")

            # Get the EMI record with org filtering
            emi = db.query(LoanMemberEmi).filter(LoanMemberEmi.id == emi_id).first()
            if not emi:
                logger.error(f"EMI not found: {emi_id}")
                print(f"EMI not found: {emi_id}")
                return {}
            
            # Verify the EMI belongs to the user's org
            loan = db.query(Loan).filter(Loan.id == emi.loan_id).first()
            if not loan or (org and loan.org != org):
                logger.error(f"EMI {emi_id} does not belong to org {org}")
                return {}

            # Update EMI status and label
            emi.emi_status = 'PAID'
            emi.label = 'PAID'
            emi.updated_at = datetime.now()

            # Get the loan member to update collected and pending amounts
            loan_member = db.query(LoanMember).filter(LoanMember.loan_id == emi.loan_id , LoanMember.member_id == emi.member_id).first()
            if loan_member:
                billing_created_by = credit_officer or paid_by
                billing_staff_id = credit_officer or None

                # Update collected and pending amounts
                loan_member.collected = float(loan_member.collected or 0) + float(amount)
                loan_member.pending = float(loan_member.pending or 0) - float(amount)
                if loan_member.pending < 0:
                    loan_member.pending = 0
                print(f"Updated loan member {loan_member.id}: collected={loan_member.collected}, pending={loan_member.pending}")

                # Create billing entry for payment (CREDIT)
                BillingService.create_payment_billing(
                    db=db,
                    loan_id=emi.loan_id,
                    member_id=emi.member_id,
                    member_group_id=loan_member.member_group_id,
                    amount=amount,
                    org=org,
                    created_by=billing_created_by,
                    staff_id=billing_staff_id,
                )

                # If loan advance provided, update advance and create billing entry
                if float(loan_advance or 0) > 0:
                    loan_member.advance = float(getattr(loan_member, 'advance', 0) or 0) + float(loan_advance)

                    BillingService.create_billing_entry(
                        db=db,
                        loan_id=emi.loan_id,
                        member_id=emi.member_id,
                        member_group_id=loan_member.member_group_id,
                        amount=float(loan_advance),
                        billing_code="LOAN_ADVANCE",
                        type="CREDIT",
                        description="Loan advance received",
                        org=org,
                        created_by=billing_created_by,
                        staff_id=billing_staff_id,
                    )

            db.commit()
            db.refresh(emi)

            print(f"Successfully processed payment for EMI ID: {emi_id}")
            return {
                'id': emi.id,
                'emi_status': emi.emi_status,
                'label': emi.label,
                'member_collected': float(loan_member.collected or 0) if loan_member else 0,
                'member_pending': float(loan_member.pending or 0) if loan_member else 0,
                'member_advance': float(getattr(loan_member, 'advance', 0) or 0) if loan_member else 0,
            }

        except Exception as e:
            logger.exception(f"Error processing EMI payment: {str(e)}")
            db.rollback()
            return {}
