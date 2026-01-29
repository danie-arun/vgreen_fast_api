from sqlalchemy.orm import Session
from models.billing import Billing
from models.loan import Loan
from models.loan_member import LoanMember
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BillingService:
    @staticmethod
    def create_billing_entry(
        db: Session,
        loan_id: int,
        member_id: int,
        amount: float,
        billing_code: str,
        type: str,
        description: str = None,
        member_group_id: int = None,
        created_by: str = "System"
    ) -> dict:
        """Create a billing entry"""
        logger.info(f"Creating billing entry for loan_id: {loan_id}, member_id: {member_id}, billing_code: {billing_code}")
        try:
            billing = Billing(
                loan_id=loan_id,
                member_id=member_id,
                member_group_id=member_group_id,
                amount=float(amount),
                billing_code=billing_code,
                type=type,
                description=description,
                created_by=created_by,
                created_at=datetime.utcnow(),
            )
            db.add(billing)
            db.commit()
            db.refresh(billing)
            logger.info(f"Successfully created billing entry: {billing.id}")
            return {
                'id': billing.id,
                'loan_id': billing.loan_id,
                'member_id': billing.member_id,
                'member_group_id': billing.member_group_id,
                'amount': float(billing.amount),
                'billing_code': billing.billing_code,
                'type': billing.type,
            }
        except Exception as e:
            logger.exception(f"Error creating billing entry: {str(e)}")
            db.rollback()
            return {}

    @staticmethod
    def create_loan_approval_billing(
        db: Session,
        loan_id: int,
        created_by: str = "System"
    ) -> list:
        """Create billing entries when loan is approved"""
        logger.info(f"Creating approval billing entries for loan_id: {loan_id}")
        try:
            # Get loan details
            loan = db.query(Loan).filter(Loan.id == loan_id).first()
            if not loan:
                logger.error(f"Loan not found: {loan_id}")
                return []

            # Get loan members
            loan_members = db.query(LoanMember).filter(LoanMember.loan_id == loan_id).all()
            if not loan_members:
                logger.warning(f"No loan members found for loan_id: {loan_id}")
                return []

            billing_entries = []

            # Create billing entries for each member
            for loan_member in loan_members:
                # 1. Loan Amount (DEBIT)
                loan_amount_entry = BillingService.create_billing_entry(
                    db=db,
                    loan_id=loan_id,
                    member_id=loan_member.member_id,
                    member_group_id=loan_member.member_group_id,
                    amount=float(loan_member.amount),
                    billing_code="LOAN_AMOUNT",
                    type="DEBIT",
                    description=f"Loan amount for member {loan_member.name}",
                    created_by=created_by
                )
                if loan_amount_entry:
                    billing_entries.append(loan_amount_entry)

                # 2. Processing Fee (DEBIT)
                processing_fee = float(loan.processing_fees or 0)
                if processing_fee > 0:
                    processing_fee_entry = BillingService.create_billing_entry(
                        db=db,
                        loan_id=loan_id,
                        member_id=loan_member.member_id,
                        member_group_id=loan_member.member_group_id,
                        amount=processing_fee,
                        billing_code="PROCESSING_FEE",
                        type="CREDIT",
                        description=f"Processing fee for member {loan_member.name}",
                        created_by=created_by
                    )
                    if processing_fee_entry:
                        billing_entries.append(processing_fee_entry)

                # 3. Insurance Fee (DEBIT)
                insurance_fee = float(loan.insurance_fees or 0)
                if insurance_fee > 0:
                    insurance_fee_entry = BillingService.create_billing_entry(
                        db=db,
                        loan_id=loan_id,
                        member_id=loan_member.member_id,
                        member_group_id=loan_member.member_group_id,
                        amount=insurance_fee,
                        billing_code="INSURANCE_FEE",
                        type="DEBIT",
                        description=f"Insurance fee for member {loan_member.name}",
                        created_by=created_by
                    )
                    if insurance_fee_entry:
                        billing_entries.append(insurance_fee_entry)

                # 4. Other Fee (DEBIT)
                other_fee = float(loan.other_fees or 0)
                if other_fee > 0:
                    other_fee_entry = BillingService.create_billing_entry(
                        db=db,
                        loan_id=loan_id,
                        member_id=loan_member.member_id,
                        member_group_id=loan_member.member_group_id,
                        amount=other_fee,
                        billing_code="OTHER_FEE",
                        type="CREDIT",
                        description=f"Other fee for member {loan_member.name}",
                        created_by=created_by
                    )
                    if other_fee_entry:
                        billing_entries.append(other_fee_entry)
                # 5. Intrest (Credit)
                interest_fee = float(loan.interest_amount or 0)
                if interest_fee > 0:
                    interest_fee_entry = BillingService.create_billing_entry(
                        db=db,
                        loan_id=loan_id,
                        member_id=loan_member.member_id,
                        member_group_id=loan_member.member_group_id,
                        amount=interest_fee,
                        billing_code="INTEREST",
                        type="CREDIT",
                        description=f"Interest for member {loan_member.name}",
                        created_by=created_by
                    )
                    if interest_fee_entry:
                        billing_entries.append(interest_fee_entry)

            logger.info(f"Successfully created {len(billing_entries)} billing entries for loan_id: {loan_id}")
            return billing_entries

        except Exception as e:
            logger.exception(f"Error creating approval billing entries: {str(e)}")
            return []

    @staticmethod
    def create_payment_billing(
        db: Session,
        loan_id: int,
        member_id: int,
        member_group_id: int,
        amount: float,
        created_by: str = "System"
    ) -> dict:
        """Create billing entry when payment is made"""
        logger.info(f"Creating payment billing entry for loan_id: {loan_id}, member_id: {member_id}, amount: {amount}")
        try:
            # Create CREDIT entry for payment
            payment_entry = BillingService.create_billing_entry(
                db=db,
                loan_id=loan_id,
                member_id=member_id,
                member_group_id=member_group_id,
                amount=amount,
                billing_code="PAYMENT",
                type="CREDIT",
                description=f"Payment received",
                created_by=created_by
            )
            logger.info(f"Successfully created payment billing entry")
            return payment_entry

        except Exception as e:
            logger.exception(f"Error creating payment billing entry: {str(e)}")
            return {}

    @staticmethod
    def get_billing_by_loan(db: Session, loan_id: int) -> list:
        """Get all billing entries for a loan"""
        logger.info(f"Fetching billing entries for loan_id: {loan_id}")
        try:
            billings = db.query(Billing).filter(Billing.loan_id == loan_id).all()
            return [
                {
                    'id': b.id,
                    'loan_id': b.loan_id,
                    'member_id': b.member_id,
                    'member_group_id': b.member_group_id,
                    'amount': float(b.amount),
                    'billing_code': b.billing_code,
                    'type': b.type,
                    'description': b.description,
                    'created_at': b.created_at.isoformat() if b.created_at else None,
                    'created_by': b.created_by,
                }
                for b in billings
            ]
        except Exception as e:
            logger.exception(f"Error fetching billing entries: {str(e)}")
            return []

    @staticmethod
    def get_billing_by_member(db: Session, loan_id: int, member_id: int) -> list:
        """Get all billing entries for a member in a loan"""
        logger.info(f"Fetching billing entries for loan_id: {loan_id}, member_id: {member_id}")
        try:
            billings = db.query(Billing).filter(
                Billing.loan_id == loan_id,
                Billing.member_id == member_id
            ).all()
            return [
                {
                    'id': b.id,
                    'loan_id': b.loan_id,
                    'member_id': b.member_id,
                    'member_group_id': b.member_group_id,
                    'amount': float(b.amount),
                    'billing_code': b.billing_code,
                    'type': b.type,
                    'description': b.description,
                    'created_at': b.created_at.isoformat() if b.created_at else None,
                    'created_by': b.created_by,
                }
                for b in billings
            ]
        except Exception as e:
            logger.exception(f"Error fetching billing entries: {str(e)}")
            return []
