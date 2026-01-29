from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.loan_member_emi import LoanMemberEmiResponse
from services.loan_member_emi_service import LoanMemberEmiService

router = APIRouter(prefix="/api/loan-member-emi", tags=["loan_member_emi"])


@router.post("/generate/{loan_id}", response_model=list[LoanMemberEmiResponse])
def generate_emi_schedule(loan_id: int, created_by: str = Query(...), db: Session = Depends(get_db)):
    """Generate EMI schedule for a loan"""
    emi_records = LoanMemberEmiService.generate_emi_schedule(db, loan_id, created_by)
    if not emi_records:
        raise HTTPException(status_code=404, detail="Could not generate EMI schedule for this loan")
    return emi_records


@router.get("/loan/{loan_id}", response_model=list[LoanMemberEmiResponse])
def get_emi_schedule_for_loan(loan_id: int, skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get EMI schedule for a specific loan"""
    emi_records = LoanMemberEmiService.get_emi_schedule_for_loan(db, loan_id)
    return emi_records[skip : skip + limit]


@router.get("/member/{loan_member_id}", response_model=list[LoanMemberEmiResponse])
def get_emi_schedule_for_member(loan_member_id: int, skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get EMI schedule for a specific loan member"""
    emi_records = LoanMemberEmiService.get_emi_schedule_for_member(db, loan_member_id)
    return emi_records[skip : skip + limit]


@router.put("/{emi_id}", response_model=LoanMemberEmiResponse)
def update_emi_collection(emi_id: int, collected_amount: float = Query(...), updated_by: str = Query(...), db: Session = Depends(get_db)):
    """Update collected amount for an EMI"""
    from decimal import Decimal
    emi = LoanMemberEmiService.update_emi_collection(db, emi_id, Decimal(str(collected_amount)), updated_by)
    if not emi:
        raise HTTPException(status_code=404, detail="EMI record not found")
    return emi


@router.delete("/loan/{loan_id}")
def delete_emi_schedule(loan_id: int, db: Session = Depends(get_db)):
    """Delete EMI schedule for a loan"""
    count = LoanMemberEmiService.delete_emi_schedule(db, loan_id)
    return {"message": f"Deleted {count} EMI records", "count": count}
