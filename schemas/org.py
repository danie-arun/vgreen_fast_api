from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrgCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    org_type: Optional[str] = None
    email: Optional[str] = None
    client_id: str
    api_token: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[int] = None

class OrgUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    org_type: Optional[str] = None
    email: Optional[str] = None
    client_id: Optional[str] = None
    api_token: Optional[str] = None
    status: Optional[str] = None
    updated_by: Optional[int] = None

class OrgResponse(BaseModel):
    id: int
    name: Optional[str]
    description: Optional[str]
    org_type: Optional[str]
    email: Optional[str]
    client_id: Optional[str]
    api_token: Optional[str]
    status: Optional[str]
    del_mark: Optional[str]
    date_created: Optional[datetime]
    date_updated: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True
