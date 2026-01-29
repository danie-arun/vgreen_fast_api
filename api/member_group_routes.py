from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.member_group import MemberGroupCreate, MemberGroupUpdate, MemberGroupResponse
from services.member_group_service import MemberGroupService

router = APIRouter(prefix="/api/member-groups", tags=["member-groups"])


@router.post("/", response_model=MemberGroupResponse)
def create_group(group: MemberGroupCreate, db: Session = Depends(get_db)):
    """Create a new member group"""
    try:
        db_group = MemberGroupService.create_group(db, group)
        return db_group
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[MemberGroupResponse])
def get_groups(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all active member groups"""
    try:
        groups = MemberGroupService.get_groups(db, skip, limit)
        return groups
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{group_id}", response_model=MemberGroupResponse)
def get_group(group_id: int, db: Session = Depends(get_db)):
    """Get a member group by ID"""
    db_group = MemberGroupService.get_group(db, group_id)
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group


@router.put("/{group_id}", response_model=MemberGroupResponse)
def update_group(
    group_id: int,
    group_update: MemberGroupUpdate,
    db: Session = Depends(get_db)
):
    """Update a member group"""
    db_group = MemberGroupService.update_group(db, group_id, group_update)
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group


@router.delete("/{group_id}")
def delete_group(
    group_id: int,
    deleted_by: str = Query(...),
    db: Session = Depends(get_db)
):
    """Soft delete a member group (deactivate)"""
    db_group = MemberGroupService.delete_group(db, group_id, deleted_by)
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"message": "Group deactivated successfully", "group_id": group_id}


@router.post("/{group_id}/reactivate")
def reactivate_group(
    group_id: int,
    reactivated_by: str = Query(...),
    db: Session = Depends(get_db)
):
    """Reactivate a deleted member group"""
    db_group = MemberGroupService.reactivate_group(db, group_id, reactivated_by)
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"message": "Group reactivated successfully", "group_id": group_id}


@router.get("/search/query", response_model=list[MemberGroupResponse])
def search_groups(
    q: str = Query(...),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """Search member groups by name or place"""
    try:
        groups = MemberGroupService.search_groups(db, q, skip, limit)
        return groups
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
