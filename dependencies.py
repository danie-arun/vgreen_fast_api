from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)


def get_db():
    """Get database session with proper error handling"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        try:
            db.rollback()
        except Exception as rollback_error:
            logger.error(f"Error during rollback: {str(rollback_error)}")
        raise
    finally:
        try:
            db.close()
        except Exception as close_error:
            logger.error(f"Error closing database session: {str(close_error)}")
            try:
                db.rollback()
            except Exception:
                pass
            try:
                db.expunge_all()
            except Exception:
                pass


def get_api_key(x_api_key: str = Header(None)) -> str:
    """
    Extract API key from X-Api-Key header.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Api-Key header is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return x_api_key


def get_current_user(
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get current user from API key.
    This dependency validates the API key and returns user details.
    """
    return AuthService.get_user_details(db, api_key)


def get_org_id(
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
) -> str:
    """
    Get organization ID from API key.
    This dependency extracts org from the authenticated user.
    """
    return AuthService.get_org_from_api_key(db, api_key)
