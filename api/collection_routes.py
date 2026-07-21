from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user, get_org_id
from services.collection_service import CollectionService

router = APIRouter(prefix="/api/collections", tags=["collections"])


class PaymentRequest(BaseModel):
    emi_id: int
    amount: float
    paid_by: str = "System"
    loan_advance: float = 0
    credit_officer: str = ""


@router.get("/list")
def get_collection_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    org: str = Depends(get_org_id)
):
    """
    Get collection list with approved loans only for authenticated user's org.
    Combines loans, loan_members, and loan_member_emi data.
    Returns list of collections with all member and EMI details.
    """
    collections = CollectionService.get_collection_list(db, org=org, skip=skip, limit=limit)
    return {
        "success": True,
        "data": collections,
        "count": len(collections)
    }


@router.get("/{loan_id}")
def get_collection_details(
    loan_id: int,
    db: Session = Depends(get_db),
    org: str = Depends(get_org_id)
):
    """Get collection details for a specific loan for authenticated user's org"""
    collection = CollectionService.get_collection_by_loan_id(db, loan_id, org=org)
    if not collection:
        return {
            "success": False,
            "message": "Collection not found",
            "data": {}
        }
    return {
        "success": True,
        "data": collection
    }


@router.post("/payment/process")
def process_emi_payment(
    payment: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Process EMI payment and update status for authenticated user's org"""
    try:
        result = CollectionService.process_emi_payment(
            db,
            payment.emi_id,
            payment.amount,
            payment.paid_by,
            org=current_user['org'],
            loan_advance=payment.loan_advance,
            credit_officer=payment.credit_officer,
        )
        if result:
            return {
                "success": True,
                "message": "Payment processed successfully",
                "data": result
            }
        else:
            return {
                "success": False,
                "message": "Failed to process payment",
                "data": {}
            }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }
