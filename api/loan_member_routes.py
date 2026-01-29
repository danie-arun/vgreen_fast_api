from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.loan_member import LoanMemberResponse
from services.loan_member_service import LoanMemberService

router = APIRouter(prefix="/api/loan-members", tags=["loan-members"])


@router.get("/loan/{loan_id}", response_model=list[LoanMemberResponse])
def get_loan_members(loan_id: int, db: Session = Depends(get_db)):
    """Get all members for a specific loan"""
    loan_members = LoanMemberService.get_loan_members(db, loan_id)
    return loan_members


@router.get("/group/{member_group_id}", response_model=list[LoanMemberResponse])
def get_loan_members_by_group(member_group_id: int, db: Session = Depends(get_db)):
    """Get all loan members for a specific member group"""
    loan_members = LoanMemberService.get_loan_members_by_group(db, member_group_id)
    return loan_members
