from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class WorkoutBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., gt=0)

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, min_length=1)
    duration_minutes: Optional[int] = Field(None, gt=0)

class WorkoutResponse(WorkoutBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True
