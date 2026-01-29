from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.staff_schema import StaffCreate, StaffUpdate, StaffResponse
from services.staff_service import StaffService

router = APIRouter(prefix="/api/staff", tags=["staff"])


@router.post("/", response_model=StaffResponse)
def create_staff(staff: StaffCreate, db: Session = Depends(get_db)):
    """Create a new staff member"""
    # Check if email already exists
    existing_staff = StaffService.get_staff_by_email(db, staff.email)
    if existing_staff:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_staff = StaffService.create_staff(db, staff)
    return db_staff


@router.get("/{staff_id}", response_model=StaffResponse)
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    """Get a staff member by ID"""
    db_staff = StaffService.get_staff(db, staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return db_staff


@router.get("/", response_model=list[StaffResponse])
def get_all_staff(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Get all active staff members"""
    staff = StaffService.get_all_staff(db, skip, limit)
    return staff


@router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(staff_id: int, staff: StaffUpdate, db: Session = Depends(get_db)):
    """Update a staff member"""
    db_staff = StaffService.update_staff(db, staff_id, staff)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return db_staff


@router.delete("/{staff_id}", response_model=StaffResponse)
def delete_staff(staff_id: int, deleted_by: str = Query(...), db: Session = Depends(get_db)):
    """Soft delete a staff member"""
    db_staff = StaffService.delete_staff(db, staff_id, deleted_by)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return db_staff


@router.get("/search/query", response_model=list[StaffResponse])
def search_staff(q: str = Query(...), skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    """Search staff by name, email, or staff_id"""
    staff = StaffService.search_staff(db, q, skip, limit)
    return staff
