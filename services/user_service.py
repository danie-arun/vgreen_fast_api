from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from passlib.hash import pbkdf2_sha256
import secrets
from datetime import datetime

class UserService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pbkdf2_sha256.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            if not hashed_password:
                return False
            return pbkdf2_sha256.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    @staticmethod
    def generate_api_key() -> str:
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        hashed_password = UserService.hash_password(user.password)
        api_key = UserService.generate_api_key()
        db_user = User(
            org=user.org,
            full_name=user.full_name,
            username=user.username,
            user_pass=hashed_password,
            role=user.role,
            created_by=user.created_by,
            api_key=api_key,
            date_created=datetime.now(),
            status="A"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_api_key(db: Session, api_key: str) -> User:
        return db.query(User).filter(User.api_key == api_key).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 10) -> list:
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_users_by_org(db: Session, org: str, skip: int = 0, limit: int = 10) -> list:
        return db.query(User).filter(User.org == org).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["user_pass"] = UserService.hash_password(update_data.pop("password"))
        
        update_data["date_updated"] = datetime.now()
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def soft_delete_user(db: Session, user_id: int, updated_by: str) -> bool:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db_user.del_mark = "Y"
        db_user.status = "I"
        db_user.updated_by = updated_by
        db_user.date_updated = datetime.now()
        db.add(db_user)
        db.commit()
        return True
    
    @staticmethod
    def hard_delete_user(db: Session, user_id: int) -> bool:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
