from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user, get_org_id
from services.billing_service import BillingService
from schemas.billing_schema import BillingCreate, BillingResponse

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/list")
def get_all_billing(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    org: str = Depends(get_org_id)
):
    """Get all billing entries for authenticated user's org"""
    try:
        billings = BillingService.get_all_billing(db, org=org, skip=skip, limit=limit)
        return {
            "success": True,
            "data": billings,
            "count": len(billings)
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "data": []
        }


@router.get("/loan/{loan_id}")
def get_billing_by_loan(
    loan_id: int,
    db: Session = Depends(get_db)
):
    """Get all billing entries for a specific loan"""
    try:
        billings = BillingService.get_billing_by_loan(db, loan_id)
        return {
            "success": True,
            "data": billings,
            "count": len(billings)
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "data": []
        }


@router.get("/loan/{loan_id}/member/{member_id}")
def get_billing_by_member(
    loan_id: int,
    member_id: int,
    db: Session = Depends(get_db)
):
    """Get all billing entries for a specific member in a loan"""
    try:
        billings = BillingService.get_billing_by_member(db, loan_id, member_id)
        return {
            "success": True,
            "data": billings,
            "count": len(billings)
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "data": []
        }


@router.post("/create")
def create_billing_entry(
    billing: BillingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new billing entry"""
    try:
        # Override org with authenticated user's org
        billing.org = current_user['org']
        result = BillingService.create_billing_entry(
            db=db,
            loan_id=billing.loan_id,
            member_id=billing.member_id,
            member_group_id=billing.member_group_id,
            staff_id=billing.staff_id,
            amount=billing.amount,
            billing_code=billing.billing_code,
            type=billing.type,
            description=billing.description,
            org=billing.org,
            created_by=billing.created_by
        )
        if result:
            return {
                "success": True,
                "message": "Billing entry created successfully",
                "data": result
            }
        else:
            return {
                "success": False,
                "message": "Failed to create billing entry",
                "data": {}
            }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }
