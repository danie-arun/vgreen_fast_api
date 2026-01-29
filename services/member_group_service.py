from sqlalchemy.orm import Session
from models.member_group import MemberGroup
from schemas.member_group import MemberGroupCreate, MemberGroupUpdate
from datetime import datetime


class MemberGroupService:
    @staticmethod
    def create_group(db: Session, group: MemberGroupCreate) -> MemberGroup:
        """Create a new member group"""
        db_group = MemberGroup(
            name=group.name,
            place=group.place,
            group_id=group.group_id,
            member_ids=group.member_ids,
            status='A',
            del_mark='N',
            created_by=group.created_by,
        )
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group

    @staticmethod
    def get_group(db: Session, group_id: int) -> MemberGroup:
        """Get a group by ID"""
        return db.query(MemberGroup).filter(
            MemberGroup.id == group_id,
            MemberGroup.del_mark == 'N'
        ).first()

    @staticmethod
    def get_groups(db: Session, skip: int = 0, limit: int = 100) -> list:
        """Get all active groups"""
        return db.query(MemberGroup).filter(
            MemberGroup.del_mark == 'N'
        ).order_by(MemberGroup.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_group(db: Session, group_id: int, group_update: MemberGroupUpdate) -> MemberGroup:
        """Update a group"""
        db_group = MemberGroupService.get_group(db, group_id)
        if not db_group:
            return None

        update_data = group_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(db_group, field, value)

        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group

    @staticmethod
    def delete_group(db: Session, group_id: int, deleted_by: str) -> MemberGroup:
        """Soft delete a group (set del_mark='Y' and status='I')"""
        db_group = MemberGroupService.get_group(db, group_id)
        if not db_group:
            return None

        db_group.del_mark = 'Y'
        db_group.status = 'I'
        db_group.updated_by = deleted_by
        db_group.updated_at = datetime.utcnow()

        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group

    @staticmethod
    def reactivate_group(db: Session, group_id: int, reactivated_by: str) -> MemberGroup:
        """Reactivate a deleted group (set del_mark='N' and status='A')"""
        db_group = db.query(MemberGroup).filter(MemberGroup.id == group_id).first()
        if not db_group:
            return None

        db_group.del_mark = 'N'
        db_group.status = 'A'
        db_group.updated_by = reactivated_by
        db_group.updated_at = datetime.utcnow()

        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group

    @staticmethod
    def search_groups(db: Session, search_query: str, skip: int = 0, limit: int = 100) -> list:
        """Search groups by name or place"""
        return db.query(MemberGroup).filter(
            (MemberGroup.name.ilike(f"%{search_query}%") |
             MemberGroup.place.ilike(f"%{search_query}%")),
            MemberGroup.del_mark == 'N'
        ).offset(skip).limit(limit).all()
