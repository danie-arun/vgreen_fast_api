from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class MemberGroupBase(BaseModel):
    name: str
    place: Optional[str] = None
    group_id: Optional[str] = None
    member_ids: Optional[Union[List[Dict[str, Any]], List[int], str]] = None


class MemberGroupCreate(MemberGroupBase):
    created_by: str


class MemberGroupUpdate(BaseModel):
    name: Optional[str] = None
    place: Optional[str] = None
    group_id: Optional[str] = None
    member_ids: Optional[Union[List[Dict[str, Any]], List[int], str]] = None
    updated_by: Optional[str] = None


class MemberGroupResponse(MemberGroupBase):
    id: int
    status: str
    del_mark: str
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    @field_validator('member_ids', mode='before')
    @classmethod
    def validate_member_ids(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                import json
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except:
                return []
        return []

    class Config:
        from_attributes = True
