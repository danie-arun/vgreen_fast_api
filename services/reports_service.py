from sqlalchemy.orm import Session
from datetime import date
from models.loan import Loan
from models.loan_member import LoanMember
from models.member_group import MemberGroup
from models.staff import Staff
from models.loan_member_emi import LoanMemberEmi
from models.billing import Billing
import logging

logger = logging.getLogger(__name__)


class ReportsService:
    @staticmethod
    def get_filter_options(db: Session):
        """Get all available filter options"""
        try:
            # Get unique EMI days (only active loans)
            emi_days = db.query(Loan.emi_day).distinct().filter(
                Loan.emi_day.isnot(None),
                Loan.del_mark == 'N'
            ).all()
            emi_days = sorted(list(set([day[0] for day in emi_days if day[0]])))

            # Get unique members (only from active loans)
            members = db.query(LoanMember.id, LoanMember.name).distinct().filter(
                LoanMember.id.in_(
                    db.query(LoanMember.id).join(Loan).filter(Loan.del_mark == 'N')
                )
            ).all()
            members_dict = {m[0]: {"id": m[0], "name": m[1]} for m in members}
            members_list = sorted(list(members_dict.values()), key=lambda x: x['name'])

            # Get unique member groups (only active groups)
            groups = db.query(MemberGroup.id, MemberGroup.name).distinct().filter(
                MemberGroup.id.in_(
                    db.query(Loan.member_group_id).filter(Loan.del_mark == 'N').distinct()
                )
            ).all()
            groups_dict = {g[0]: {"id": g[0], "name": g[1]} for g in groups}
            groups_list = sorted(list(groups_dict.values()), key=lambda x: x['name'])

            # Get unique staffs (only from active loans)
            staffs = db.query(Staff.staff_id, Staff.name, Staff.designation).distinct().filter(
                Staff.staff_id.in_(
                    db.query(Loan.assign_to).filter(
                        Loan.del_mark == 'N',
                        Loan.assign_to.isnot(None)
                    ).distinct()
                )
            ).all()
            staffs_dict = {s[0]: {"id": s[0], "name": f"{s[1]} ({s[2]}"} for s in staffs}
            staffs_list = sorted(list(staffs_dict.values()), key=lambda x: x['name'])

            # Get unique loan numbers (only active loans)
            loans = db.query(Loan.id, Loan.loan_id).distinct().filter(
                Loan.del_mark == 'N'
            ).all()
            loans_dict = {l[0]: {"id": l[0], "loan_id": l[1]} for l in loans}
            loans_list = sorted(list(loans_dict.values()), key=lambda x: x['loan_id'])

            return {
                "emi_days": emi_days,
                "members": members_list,
                "member_groups": groups_list,
                "staffs": staffs_list,
                "loans": loans_list,
            }
        except Exception as e:
            logger.exception(f"Error fetching filter options: {str(e)}")
            return {
                "emi_days": [],
                "members": [],
                "member_groups": [],
                "staffs": [],
                "loans": [],
            }

    @staticmethod
    def get_reports_data(
        db: Session,
        start_date: date = None,
        end_date: date = None,
        emi_days: list = None,
        member_ids: list = None,
        group_ids: list = None,
        staff_ids: list = None,
        loan_ids: list = None,
    ):
        """Get reports data with filters applied"""
        try:
            # Build base query
            query = db.query(Loan).filter(Loan.del_mark == "N")

            # Apply date range filter
            if start_date:
                query = query.filter(Loan.created_at >= start_date)
            if end_date:
                query = query.filter(Loan.created_at <= end_date)

            # Apply EMI day filter
            if emi_days:
                query = query.filter(Loan.emi_day.in_(emi_days))

            # Apply staff filter
            if staff_ids:
                query = query.filter(Loan.assign_to.in_(staff_ids))

            # Apply loan ID filter
            if loan_ids:
                query = query.filter(Loan.id.in_(loan_ids))

            loans = query.all()

            # Filter by member groups and members (requires joining with LoanMember)
            if group_ids or member_ids:
                filtered_loans = []
                for loan in loans:
                    loan_members = db.query(LoanMember).filter(
                        LoanMember.loan_id == loan.id
                    ).all()

                    if group_ids:
                        loan_members = [
                            m for m in loan_members if m.member_group_id in group_ids
                        ]

                    if member_ids:
                        loan_members = [m for m in loan_members if m.id in member_ids]

                    if loan_members:
                        filtered_loans.append(loan)

                loans = filtered_loans if filtered_loans else []

            # Calculate metrics
            metrics = ReportsService._calculate_metrics(db, loans)

            # Get summary data
            summary_data = ReportsService._get_summary_data(db, loans)
            
            # Get user summary data
            user_summary_data = ReportsService._get_user_summary_data(db, loans)
            
            # Get EMI summary data
            emi_summary_data = ReportsService._get_emi_summary_data(db, loans)
            
            # Get collections summary data
            collections_summary_data = ReportsService._get_collections_summary_data(db, loans)

            return {
                "metrics": metrics,
                "summary_data": summary_data,
                "user_summary_data": user_summary_data,
                "emi_summary_data": emi_summary_data,
                "collections_summary_data": collections_summary_data,
                "loans_count": len(loans),
            }

        except Exception as e:
            logger.exception(f"Error fetching reports data: {str(e)}")
            return {
                "metrics": {},
                "summary_data": [],
                "loans_count": 0,
            }

    @staticmethod
    def _calculate_metrics(db: Session, loans: list):
        """Calculate metrics from billing table"""
        try:
            loan_ids = [loan.id for loan in loans]
            
            if not loan_ids:
                return {
                    "totalLoanAmount": 0,
                    "totalCollected": 0,
                    "totalPending": 0,
                    "totalInterestFees": 0,
                    "totalLoans": 0,
                    "totalMembers": 0,
                }

            # Get billing records for the loans
            billing_records = db.query(Billing).filter(
                Billing.loan_id.in_(loan_ids)
            ).all()

            # Calculate metrics based on billing_code
            total_loan_amount = 0
            total_collected = 0
            total_interest_fees = 0

            for billing in billing_records:
                amount = float(billing.amount or 0)
                
                if billing.billing_code == "LOAN_AMOUNT":
                    total_loan_amount += amount
                elif billing.billing_code == "PAYMENT":
                    total_collected += amount
                elif billing.billing_code in ["PROCESSING_FEE", "INSURANCE_FEE", "OTHER_FEE", "INTEREST"]:
                    total_interest_fees += amount

            # Calculate pending amount
            total_pending = total_loan_amount - total_collected

            # Count total members and unique member groups
            total_members = 0
            member_group_ids = set()
            for loan in loans:
                loan_members = db.query(LoanMember).filter(
                    LoanMember.loan_id == loan.id
                ).all()
                total_members += len(loan_members)
                
                # Collect unique member group IDs
                for member in loan_members:
                    if member.member_group_id:
                        member_group_ids.add(member.member_group_id)

            total_member_groups = len(member_group_ids)

            return {
                "totalLoanAmount": round(total_loan_amount, 2),
                "totalCollected": round(total_collected, 2),
                "totalPending": round(total_pending, 2),
                "totalInterestFees": round(total_interest_fees, 2),
                "totalLoans": len(loans),
                "totalMemberGroups": total_member_groups,
                "totalMembers": total_members,
            }
        except Exception as e:
            logger.exception(f"Error calculating metrics: {str(e)}")
            return {}

    @staticmethod
    def _get_summary_data(db: Session, loans: list):
        """Get summary data for table"""
        try:
            summary = []
            for idx, loan in enumerate(loans, 1):
                loan_members = db.query(LoanMember).filter(
                    LoanMember.loan_id == loan.id
                ).all()

                member_names = ", ".join([m.name for m in loan_members])
                member_count = len(loan_members)
                
                group = db.query(MemberGroup).filter(
                    MemberGroup.id == loan.member_group_id
                ).first()

                # Calculate loan totals from EMI records
                total_collected = 0
                total_pending = 0
                total_overdue = 0

                emi_records = db.query(LoanMemberEmi).filter(
                    LoanMemberEmi.loan_id == loan.id
                ).all()

                for emi in emi_records:
                    if emi.emi_status == "PAID":
                        total_collected += float(emi.emi_amount or 0)
                    elif emi.emi_status == "OVERDUE":
                        total_overdue += float(emi.emi_amount or 0)
                    else:
                        total_pending += float(emi.emi_amount or 0)

                # Calculate total loan amount as loan_amount × number of members
                base_loan_amount = float(loan.loan_amount or 0)
                total_loan_amount = base_loan_amount * member_count

                # Calculate total interest from billing table
                total_interest = 0
                try:
                    interest_records = db.query(Billing).filter(
                        Billing.loan_id == loan.id,
                        Billing.billing_code.in_(['INTEREST', 'PROCESSING_FEE', 'INSURANCE_FEE', 'OTHER_FEE'])
                    ).all()

                    for record in interest_records:
                        total_interest += float(record.amount or 0)
                except Exception as e:
                    logger.warning(f"Error calculating interest for loan {loan.id}: {str(e)}")
                    total_interest = 0

                # Format loan amount with interest breakdown
                loan_amount_display = f"{int(total_loan_amount)} + {int(total_interest)}" if total_interest > 0 else str(int(total_loan_amount))

                summary.append(
                    {
                        "id": idx,
                        "loanId": loan.loan_id,
                        "groupName": group.name if group else "N/A",
                        "members": member_names,
                        "loanAmount": loan_amount_display,
                        "loanAmountValue": total_loan_amount,
                        "interestAmount": total_interest,
                        "collectedAmount": total_collected,
                        "pendingAmount": total_pending,
                        "overdueAmount": total_overdue,
                        "emiDay": loan.emi_day or "N/A",
                        "status": loan.loan_status,
                    }
                )

            return summary
        except Exception as e:
            logger.exception(f"Error getting summary data: {str(e)}")
            return []

    @staticmethod
    def _get_user_summary_data(db: Session, loans: list):
        """Get user summary data with EMI details"""
        try:
            user_summary = []
            user_id = 1
            
            for loan in loans:
                loan_members = db.query(LoanMember).filter(
                    LoanMember.loan_id == loan.id
                ).all()
                
                group = db.query(MemberGroup).filter(
                    MemberGroup.id == loan.member_group_id
                ).first()
                
                for member in loan_members:
                    # Get EMI records for this member
                    emi_records = db.query(LoanMemberEmi).filter(
                        LoanMemberEmi.loan_id == loan.id
                    ).all()
                    
                    total_emi = sum(float(emi.emi_amount or 0) for emi in emi_records)
                    paid_emi = sum(
                        float(emi.emi_amount or 0) for emi in emi_records 
                        if emi.emi_status == "PAID"
                    )
                    pending_emi = total_emi - paid_emi
                    
                    user_summary.append({
                        "id": user_id,
                        "userName": member.name,
                        "loanId": loan.loan_id,
                        "groupName": group.name if group else "N/A",
                        "totalEmi": round(total_emi, 2),
                        "paidEmi": round(paid_emi, 2),
                        "pendingEmi": round(pending_emi, 2),
                    })
                    user_id += 1
            
            return user_summary
        except Exception as e:
            logger.exception(f"Error getting user summary data: {str(e)}")
            return []

    @staticmethod
    def _get_emi_summary_data(db: Session, loans: list):
        """Get EMI summary data with expandable EMI details"""
        try:
            emi_summary = []
            emi_id = 1
            
            for loan in loans:
                loan_members = db.query(LoanMember).filter(
                    LoanMember.loan_id == loan.id
                ).all()
                
                for member in loan_members:
                    # Get EMI records for this loan
                    emi_records = db.query(LoanMemberEmi).filter(
                        LoanMemberEmi.loan_id == loan.id
                    ).all()
                    
                    total_emis = len(emi_records)
                    paid_emis = len([e for e in emi_records if e.emi_status == "PAID"])
                    pending_emis = total_emis - paid_emis
                    
                    # Build EMI details for expansion
                    emi_details = []
                    for emi in emi_records:
                        emi_details.append({
                            "emiDate": emi.emi_date.strftime("%Y-%m-%d") if emi.emi_date else "N/A",
                            "emiAmount": round(float(emi.emi_amount or 0), 2),
                            "emiStatus": emi.emi_status,
                        })
                    
                    emi_summary.append({
                        "id": emi_id,
                        "loanId": loan.loan_id,
                        "userName": member.name,
                        "totalEmis": total_emis,
                        "paidEmis": paid_emis,
                        "pendingEmis": pending_emis,
                        "emiDetails": emi_details,
                    })
                    emi_id += 1
            
            return emi_summary
        except Exception as e:
            logger.exception(f"Error getting EMI summary data: {str(e)}")
            return []

    @staticmethod
    def _get_collections_summary_data(db: Session, loans: list):
        """Get collections summary data with per-user breakdown"""
        try:
            collections_summary = []
            collection_id = 1
            
            for loan in loans:
                loan_members = db.query(LoanMember).filter(
                    LoanMember.loan_id == loan.id
                ).all()
                
                group = db.query(MemberGroup).filter(
                    MemberGroup.id == loan.member_group_id
                ).first()
                
                # Get EMI records for this loan
                emi_records = db.query(LoanMemberEmi).filter(
                    LoanMemberEmi.loan_id == loan.id
                ).all()
                
                total_loan_amount = float(loan.loan_amount or 0)
                
                # Calculate collected and pending from EMIs
                total_collected = sum(
                    float(emi.emi_amount or 0) for emi in emi_records 
                    if emi.emi_status == "PAID"
                )
                total_pending = sum(
                    float(emi.emi_amount or 0) for emi in emi_records 
                    if emi.emi_status != "PAID"
                )
                
                # Get next EMI details
                next_emi = None
                next_emi_date = "N/A"
                next_emi_amount = 0
                
                pending_emis = [e for e in emi_records if e.emi_status != "PAID"]
                if pending_emis:
                    pending_emis.sort(key=lambda x: x.emi_date if x.emi_date else "")
                    next_emi = pending_emis[0]
                    next_emi_date = next_emi.emi_date.strftime("%Y-%m-%d") if next_emi.emi_date else "N/A"
                    next_emi_amount = float(next_emi.emi_amount or 0)
                
                # Build user details for expansion
                user_details = []
                for member in loan_members:
                    user_details.append({
                        "userName": member.name,
                        "totalEmi": round(total_loan_amount / len(loan_members), 2) if loan_members else 0,
                        "paidEmi": round(total_collected / len(loan_members), 2) if loan_members else 0,
                        "pendingEmi": round(total_pending / len(loan_members), 2) if loan_members else 0,
                    })
                
                collections_summary.append({
                    "id": collection_id,
                    "loanId": loan.loan_id,
                    "groupName": group.name if group else "N/A",
                    "loanAmount": round(total_loan_amount, 2),
                    "collectedAmount": round(total_collected, 2),
                    "pendingAmount": round(total_pending, 2),
                    "nextEmiDate": next_emi_date,
                    "nextEmiAmount": round(next_emi_amount, 2),
                    "userDetails": user_details,
                })
                collection_id += 1
            
            return collections_summary
        except Exception as e:
            logger.exception(f"Error getting collections summary data: {str(e)}")
            return []
