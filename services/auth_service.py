from sqlalchemy.orm import Session
from models.user import User
from fastapi import HTTPException, status


class AuthService:
    @staticmethod
    def get_user_by_api_key(db: Session, api_key: str) -> User:
        """
        Fetch user details from database using API key.
        Raises HTTPException if API key is invalid or user not found.
        """
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db.query(User).filter(
            User.api_key == api_key,
            User.status == 'A',
            User.del_mark == 'N'
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    @staticmethod
    def get_org_from_api_key(db: Session, api_key: str) -> str:
        """
        Get organization ID from API key.
        Returns org value from user record.
        """
        user = AuthService.get_user_by_api_key(db, api_key)
        return user.org
    
    @staticmethod
    def get_user_details(db: Session, api_key: str) -> dict:
        """
        Get complete user details from API key.
        Returns user information including org, role, and other details.
        """
        user = AuthService.get_user_by_api_key(db, api_key)
        
        return {
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "org": user.org,
            "role": user.role,
            "api_key": user.api_key,
            "status": user.status
        }
    
    @staticmethod
    def validate_api_key(db: Session, api_key: str) -> bool:
        """
        Validate if API key exists and is active.
        Returns True if valid, False otherwise.
        """
        if not api_key:
            return False
        
        user = db.query(User).filter(
            User.api_key == api_key,
            User.status == 'A',
            User.del_mark == 'N'
        ).first()
        
        return user is not None
