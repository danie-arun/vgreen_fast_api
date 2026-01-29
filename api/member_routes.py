from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.member import MemberCreate, MemberUpdate, MemberResponse
from services.member_service import MemberService

router = APIRouter(prefix="/api/members", tags=["members"])


@router.post("/", response_model=MemberResponse)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    """Create a new member"""
    try:
        # Check if member with same mobile number already exists
        existing_member = MemberService.get_member_by_mobile(db, member.primary_mobile_number)
        if existing_member:
            raise HTTPException(
                status_code=400,
                detail="Member with this mobile number already exists"
            )

        db_member = MemberService.create_member(db, member)
        return db_member
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    """Get a member by ID"""
    db_member = MemberService.get_member(db, member_id)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member


@router.get("/", response_model=list[MemberResponse])
def get_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all active members with pagination"""
    members = MemberService.get_members(db, skip=skip, limit=limit)
    return members


@router.get("/search/query", response_model=list[MemberResponse])
def search_members(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Search members by name or mobile number"""
    members = MemberService.search_members(db, q, skip=skip, limit=limit)
    return members


@router.get("/status/{status}", response_model=list[MemberResponse])
def get_members_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get members by status (A=Active, I=Inactive)"""
    if status not in ['A', 'I']:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'A' for Active or 'I' for Inactive")
    
    members = MemberService.get_members_by_status(db, status, skip=skip, limit=limit)
    return members


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    member_update: MemberUpdate,
    db: Session = Depends(get_db)
):
    """Update a member"""
    db_member = MemberService.update_member(db, member_id, member_update)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member


@router.delete("/{member_id}")
def delete_member(
    member_id: int,
    deleted_by: str = Query(...),
    db: Session = Depends(get_db)
):
    """Soft delete a member (deactivate)"""
    db_member = MemberService.delete_member(db, member_id, deleted_by)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member deactivated successfully", "member_id": member_id}


@router.post("/{member_id}/reactivate")
def reactivate_member(
    member_id: int,
    reactivated_by: str = Query(...),
    db: Session = Depends(get_db)
):
    """Reactivate a deleted member"""
    db_member = MemberService.reactivate_member(db, member_id, reactivated_by)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member reactivated successfully", "member_id": member_id}
