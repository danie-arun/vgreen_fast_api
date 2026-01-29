from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    org: Optional[str] = None
    full_name: Optional[str] = None
    username: str
    password: str
    role: Optional[str] = None
    created_by: Optional[str] = None
    del_mark: Optional[str] = None

class UserUpdate(BaseModel):
    org: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    last_active: Optional[datetime] = None
    role: Optional[str] = None
    status: Optional[str] = None
    del_mark: Optional[str] = None
    updated_by: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    org: Optional[str]
    full_name: Optional[str]
    username: Optional[str]
    role: Optional[str]
    user_pass: Optional[str] = None
    api_key: Optional[str]
    last_active: Optional[datetime]
    status: Optional[str]
    del_mark: Optional[str]
    date_created: Optional[datetime]
    date_updated: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]
    
    class Config:
        from_attributes = True
