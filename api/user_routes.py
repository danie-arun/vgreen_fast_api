from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.user import UserCreate, UserResponse, UserUpdate
from schemas.org import OrgResponse
from services.user_service import UserService
from services.org_service import OrgService
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/users", tags=["users"])

class LoginRequest(BaseModel):
    username: str
    password: str
    client_id: str

class LoginResponseSuccess(BaseModel):
    code: int
    message: str
    user_id: int
    user_name: str
    org_id: int
    org_name: str
    root_user: Optional[str]
    api_key: str
    role: Optional[str]

class LoginResponseError(BaseModel):
    code: int
    message: str

class LoginResponse(BaseModel):
    code: int
    message: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    org_id: Optional[int] = None
    org_name: Optional[str] = None
    root_user: Optional[str] = None
    api_key: Optional[str] = None
    role: Optional[str] = None

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_username = UserService.get_user_by_username(db, user.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    db_user = UserService.create_user(db, user)
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = UserService.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.get("/", response_model=list[UserResponse])
async def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = UserService.get_all_users(db, skip=skip, limit=limit)
    return users

@router.get("/org/{org}", response_model=list[UserResponse])
async def list_users_by_org(org: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = UserService.get_users_by_org(db, org, skip=skip, limit=limit)
    return users

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = UserService.update_user(db, user_id, user_update)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, updated_by: str, db: Session = Depends(get_db)):
    success = UserService.soft_delete_user(db, user_id, updated_by)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None

@router.post("/login_auth", response_model=LoginResponse)
async def login_auth(login_request: LoginRequest, db: Session = Depends(get_db)):
    db_org = OrgService.get_org_by_client_id(db, login_request.client_id)
    
    if not db_org:
        return LoginResponse(
            code=0,
            message="Invalid client ID"
        )
    
    db_user = UserService.get_user_by_username(db, login_request.username)
    
    if not db_user:
        return LoginResponse(
            code=0,
            message="Invalid username"
        )
    
    if db_user.org != str(db_org.id):
        return LoginResponse(
            code=0,
            message="User does not belong to this organization"
        )
    
    if not UserService.verify_password(login_request.password, db_user.user_pass):
        return LoginResponse(
            code=0,
            message="Invalid password"
        )
    
    return LoginResponse(
        code=1,
        message="Login successful",
        user_id=db_user.id,
        user_name=db_user.username,
        org_id=db_org.id,
        org_name=db_org.name,
        root_user=db_user.role,
        api_key=db_user.api_key,
        role=db_user.role
    )
