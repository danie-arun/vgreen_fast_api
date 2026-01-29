from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from services.reports_service import ReportsService
from services.export_service import ExportService
from datetime import date
from typing import List, Optional
import io
import os

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/filter-options")
def get_filter_options(db: Session = Depends(get_db)):
    """Get all available filter options for reports"""
    return ReportsService.get_filter_options(db)


@router.get("/data")
def get_reports_data(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    emi_days: Optional[List[str]] = Query(None),
    member_ids: Optional[List[int]] = Query(None),
    group_ids: Optional[List[int]] = Query(None),
    staff_ids: Optional[List[str]] = Query(None),
    loan_ids: Optional[List[int]] = Query(None),
):
    """Get reports data with filters applied"""
    return ReportsService.get_reports_data(
        db,
        start_date=start_date,
        end_date=end_date,
        emi_days=emi_days,
        member_ids=member_ids,
        group_ids=group_ids,
        staff_ids=staff_ids,
        loan_ids=loan_ids,
    )


@router.get("/export/financial-summary")
def export_financial_summary(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    emi_days: Optional[List[str]] = Query(None),
    member_ids: Optional[List[int]] = Query(None),
    group_ids: Optional[List[int]] = Query(None),
    staff_ids: Optional[List[str]] = Query(None),
    loan_ids: Optional[List[int]] = Query(None),
):
    """Export Financial Summary to Word document"""
    try:
        data = ReportsService.get_reports_data(
            db,
            start_date=start_date,
            end_date=end_date,
            emi_days=emi_days,
            member_ids=member_ids,
            group_ids=group_ids,
            staff_ids=staff_ids,
            loan_ids=loan_ids,
        )
        
        doc = ExportService.export_financial_summary(data['summary_data'], data['metrics'])
        
        # Save to temporary file
        temp_file = f"/tmp/financial_summary_{date.today()}.docx"
        doc.save(temp_file)
        
        return FileResponse(
            path=temp_file,
            filename=f"Financial_Summary_{date.today()}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        return {"error": str(e)}


@router.get("/export/user-summary")
def export_user_summary(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    emi_days: Optional[List[str]] = Query(None),
    member_ids: Optional[List[int]] = Query(None),
    group_ids: Optional[List[int]] = Query(None),
    staff_ids: Optional[List[str]] = Query(None),
    loan_ids: Optional[List[int]] = Query(None),
):
    """Export User Summary to Word document"""
    try:
        data = ReportsService.get_reports_data(
            db,
            start_date=start_date,
            end_date=end_date,
            emi_days=emi_days,
            member_ids=member_ids,
            group_ids=group_ids,
            staff_ids=staff_ids,
            loan_ids=loan_ids,
        )
        
        doc = ExportService.export_user_summary(data['user_summary_data'])
        
        # Save to temporary file
        temp_file = f"/tmp/user_summary_{date.today()}.docx"
        doc.save(temp_file)
        
        return FileResponse(
            path=temp_file,
            filename=f"User_Summary_{date.today()}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        return {"error": str(e)}


@router.get("/export/emi-summary")
def export_emi_summary(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    emi_days: Optional[List[str]] = Query(None),
    member_ids: Optional[List[int]] = Query(None),
    group_ids: Optional[List[int]] = Query(None),
    staff_ids: Optional[List[str]] = Query(None),
    loan_ids: Optional[List[int]] = Query(None),
):
    """Export EMI Summary to Word document"""
    try:
        data = ReportsService.get_reports_data(
            db,
            start_date=start_date,
            end_date=end_date,
            emi_days=emi_days,
            member_ids=member_ids,
            group_ids=group_ids,
            staff_ids=staff_ids,
            loan_ids=loan_ids,
        )
        
        doc = ExportService.export_emi_summary(data['emi_summary_data'])
        
        # Save to temporary file
        temp_file = f"/tmp/emi_summary_{date.today()}.docx"
        doc.save(temp_file)
        
        return FileResponse(
            path=temp_file,
            filename=f"EMI_Summary_{date.today()}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        return {"error": str(e)}


@router.get("/export/collections-summary")
def export_collections_summary(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    emi_days: Optional[List[str]] = Query(None),
    member_ids: Optional[List[int]] = Query(None),
    group_ids: Optional[List[int]] = Query(None),
    staff_ids: Optional[List[str]] = Query(None),
    loan_ids: Optional[List[int]] = Query(None),
):
    """Export Collections Summary to Word document"""
    try:
        data = ReportsService.get_reports_data(
            db,
            start_date=start_date,
            end_date=end_date,
            emi_days=emi_days,
            member_ids=member_ids,
            group_ids=group_ids,
            staff_ids=staff_ids,
            loan_ids=loan_ids,
        )
        
        doc = ExportService.export_collections_summary(data['collections_summary_data'])
        
        # Save to temporary file
        temp_file = f"/tmp/collections_summary_{date.today()}.docx"
        doc.save(temp_file)
        
        return FileResponse(
            path=temp_file,
            filename=f"Collections_Summary_{date.today()}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        return {"error": str(e)}
