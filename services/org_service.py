from sqlalchemy.orm import Session
from models.org import Org
from schemas.org import OrgCreate, OrgUpdate

class OrgService:
    
    @staticmethod
    def create_org(db: Session, org: OrgCreate) -> Org:
        db_org = Org(
            name=org.name,
            description=org.description,
            org_type=org.org_type,
            email=org.email,
            client_id=org.client_id,
            api_token=org.api_token,
            status=org.status,
            created_by=org.created_by
        )
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        return db_org
    
    @staticmethod
    def get_org_by_id(db: Session, org_id: int) -> Org:
        return db.query(Org).filter(Org.id == org_id).first()
    
    @staticmethod
    def get_org_by_client_id(db: Session, client_id: str) -> Org:
        return db.query(Org).filter(Org.client_id == client_id).first()
    
    @staticmethod
    def get_all_orgs(db: Session, skip: int = 0, limit: int = 10) -> list:
        return db.query(Org).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_org(db: Session, org_id: int, org_update: OrgUpdate) -> Org:
        db_org = OrgService.get_org_by_id(db, org_id)
        if not db_org:
            return None
        
        update_data = org_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_org, field, value)
        
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        return db_org
    
    @staticmethod
    def delete_org(db: Session, org_id: int) -> bool:
        db_org = OrgService.get_org_by_id(db, org_id)
        if not db_org:
            return False
        
        db.delete(db_org)
        db.commit()
        return True
