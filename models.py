from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from database import Base

# Roles define karte hain (Enum se strict validation hoti hai)
class RoleEnum(str, enum.Enum):
    Admin = "Admin"
    Member = "Member"

class StatusEnum(str, enum.Enum):
    Todo = "Todo"
    InProgress = "In Progress"
    Done = "Done"

# 1. User Table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.Member) # Role-based access yahan se shuru hota hai
    
    # Relationships
    projects = relationship("Project", back_populates="admin")
    tasks = relationship("Task", back_populates="assigned_user")

# 2. Project Table
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    admin_id = Column(Integer, ForeignKey("users.id")) # Har project ka ek Admin hona chahiye
    
    # Relationships
    admin = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

# 3. Task Table
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.Todo)
    project_id = Column(Integer, ForeignKey("projects.id")) # Task kis project ka hai
    assigned_to = Column(Integer, ForeignKey("users.id")) # Task kis member ko assigned hai
    due_date = Column(String, nullable=True) # NAYA: Due Date ke liye
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assigned_user = relationship("User", back_populates="tasks")
    