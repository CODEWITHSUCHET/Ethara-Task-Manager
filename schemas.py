from pydantic import BaseModel
from models import RoleEnum, StatusEnum
from typing import Optional

# 1. User Schemas
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: RoleEnum = RoleEnum.Member # Default role Member hoga

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: RoleEnum

    class Config:
        from_attributes = True

# 2. Login & Token Schemas
class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# 3. Project Schemas
class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectResponse(ProjectCreate):
    id: int
    admin_id: int
    
    class Config:
        from_attributes = True

# 4. Task Schemas
class TaskCreate(BaseModel):
    title: str
    project_id: int
    assigned_to: int # Member ki User ID
    due_date: Optional[str] = None # NAYA: Due Date yahan add ho gayi hai

class TaskResponse(TaskCreate):
    id: int
    status: StatusEnum
    
    class Config:
        from_attributes = True

class TaskStatusUpdate(BaseModel):
    status: StatusEnum
    