from sqlalchemy.orm import Session
from models.loan_member import LoanMember
from models.member import Member
from schemas.loan_member import LoanMemberCreate
from datetime import datetime


class LoanMemberService:
    @staticmethod
    def create_loan_member(db: Session, loan_member: LoanMemberCreate) -> LoanMember:
        """Create a new loan member record"""
        db_loan_member = LoanMember(
            loan_id=loan_member.loan_id,
            member_group_id=loan_member.member_group_id,
            member_id=loan_member.member_id,
            name=loan_member.name,
            place=loan_member.place,
            phone=loan_member.phone,
            amount=loan_member.amount,
            collected=0,
            pending=loan_member.amount,
            created_by=loan_member.created_by,
        )
        db.add(db_loan_member)
        db.commit()
        db.refresh(db_loan_member)
        return db_loan_member

    @staticmethod
    def create_loan_members_for_group(db: Session, loan_id: int, member_group_id: int, amount: float, created_by: str) -> list:
        """Create loan member records for all members in a member group"""
        from models.member_group import MemberGroup
        
        member_group = db.query(MemberGroup).filter(MemberGroup.id == member_group_id).first()
        if not member_group:
            return []
        
        loan_members = []
        
        if member_group.member_ids:
            for mem_id in member_group.member_ids:
                member_id = mem_id.get('id') if isinstance(mem_id, dict) else mem_id
                member = db.query(Member).filter(Member.id == member_id).first()
                
                if member:
                    full_name = member.full_name
                    if member.father_spouse_name:
                        full_name = f"{full_name} {member.father_spouse_name}"
                    
                    db_loan_member = LoanMember(
                        loan_id=loan_id,
                        member_group_id=member_group_id,
                        member_id=member.id,
                        name=full_name,
                        place=member.place,
                        phone=member.primary_mobile_number,
                        amount=amount,
                        collected=0,
                        pending=amount,
                        created_by=created_by,
                    )
                    db.add(db_loan_member)
                    loan_members.append(db_loan_member)
        
        db.commit()
        for loan_member in loan_members:
            db.refresh(loan_member)
        
        return loan_members

    @staticmethod
    def get_loan_members(db: Session, loan_id: int) -> list:
        """Get all members for a specific loan"""
        return db.query(LoanMember).filter(LoanMember.loan_id == loan_id).all()

    @staticmethod
    def get_loan_members_by_group(db: Session, member_group_id: int) -> list:
        """Get all loan members for a specific member group"""
        return db.query(LoanMember).filter(LoanMember.member_group_id == member_group_id).all()

    @staticmethod
    def delete_loan_members(db: Session, loan_id: int) -> int:
        """Delete all loan members for a specific loan"""
        count = db.query(LoanMember).filter(LoanMember.loan_id == loan_id).delete()
        db.commit()
        return count

    @staticmethod
    def update_loan_members_amount(db: Session, loan_id: int, new_amount: float) -> list:
        """Update the amount for all members of a loan"""
        loan_members = db.query(LoanMember).filter(LoanMember.loan_id == loan_id).all()
        
        for loan_member in loan_members:
            loan_member.amount = new_amount
            loan_member.pending = new_amount
        
        db.commit()
        for loan_member in loan_members:
            db.refresh(loan_member)
        
        return loan_members

    @staticmethod
    def update_loan_member_collected(db: Session, loan_member_id: int, collected_amount: float) -> LoanMember:
        """Update collected amount for a loan member"""
        loan_member = db.query(LoanMember).filter(LoanMember.id == loan_member_id).first()
        
        if loan_member:
            loan_member.collected = collected_amount
            loan_member.pending = loan_member.amount - collected_amount
            db.commit()
            db.refresh(loan_member)
        
        return loan_member

    @staticmethod
    def update_loan_members_collected_for_loan(db: Session, loan_id: int, collected_amount: float) -> list:
        """Update collected amount for all members of a loan"""
        loan_members = db.query(LoanMember).filter(LoanMember.loan_id == loan_id).all()
        
        for loan_member in loan_members:
            loan_member.collected = collected_amount
            loan_member.pending = loan_member.amount - collected_amount
        
        db.commit()
        for loan_member in loan_members:
            db.refresh(loan_member)
        
        return loan_members
