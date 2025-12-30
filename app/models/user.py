import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, String

class UserStatus(str, PyEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"

class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"

class AuthProviderEnum(str, PyEnum):
    GOOGLE = "google"
    OTP = "otp"
    EMAIL = "email"

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: Optional[str] = Field(default=None, sa_column=Column(String, unique=True, index=True, nullable=True))
    phone_number: Optional[str] = Field(default=None, sa_column=Column(String, unique=True, nullable=True))
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole = Field(default=UserRole.USER)
    is_email_verified: bool = Field(default=False)
    is_phone_verified: bool = Field(default=False)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to auth providers
    auth_providers: List["AuthProvider"] = Relationship(back_populates="user")
    
    # Relationship to sitter profile
    sitter_profile: Optional["SitterProfile"] = Relationship(back_populates="user")

class AuthProvider(SQLModel, table=True):
    __tablename__ = "auth_providers"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    provider: AuthProviderEnum
    provider_uid: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="auth_providers")
