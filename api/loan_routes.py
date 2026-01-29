from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.loan import LoanCreate, LoanUpdate, LoanResponse
from services.loan_service import LoanService

router = APIRouter(prefix="/api/loans", tags=["loans"])


@router.post("/", response_model=LoanResponse)
def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    """Create a new loan"""
    db_loan = LoanService.create_loan(db, loan)
    return db_loan


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    """Get a loan by ID"""
    db_loan = LoanService.get_loan(db, loan_id)
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return db_loan


@router.get("/", response_model=list[LoanResponse])
def get_loans(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all active loans"""
    loans = LoanService.get_loans(db, skip, limit)
    return loans


@router.get("/member/{member_id}", response_model=list[LoanResponse])
def get_loans_by_member(member_id: int, skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all loans for a specific member"""
    loans = LoanService.get_loans_by_member(db, member_id, skip, limit)
    return loans


@router.get("/group/{group_id}", response_model=list[LoanResponse])
def get_loans_by_group(group_id: int, skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all loans for a specific member group"""
    loans = LoanService.get_loans_by_group(db, group_id, skip, limit)
    return loans


@router.put("/{loan_id}", response_model=LoanResponse)
def update_loan(loan_id: int, loan: LoanUpdate, db: Session = Depends(get_db)):
    """Update a loan"""
    db_loan = LoanService.update_loan(db, loan_id, loan)
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return db_loan


@router.delete("/{loan_id}")
def delete_loan(loan_id: int, deleted_by: str = Query(...), db: Session = Depends(get_db)):
    """Soft delete a loan (deactivate)"""
    db_loan = LoanService.delete_loan(db, loan_id, deleted_by)
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return {"message": "Loan deactivated successfully", "loan_id": loan_id}


@router.post("/{loan_id}/reactivate")
def reactivate_loan(loan_id: int, reactivated_by: str = Query(...), db: Session = Depends(get_db)):
    """Reactivate a soft-deleted loan"""
    db_loan = LoanService.reactivate_loan(db, loan_id, reactivated_by)
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return {"message": "Loan reactivated successfully", "loan_id": loan_id}


@router.get("/search/query", response_model=list[LoanResponse])
def search_loans(query: str = Query(...), skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Search loans by loan_id"""
    loans = LoanService.search_loans(db, query, skip, limit)
    return loans
