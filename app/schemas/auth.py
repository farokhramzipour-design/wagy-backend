from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class GoogleAuthRequest(BaseModel):
    id_token: str

class UserResponse(BaseModel):
    id: UUID
    email: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_email_verified: bool

class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

class AuthData(BaseModel):
    user: UserResponse
    tokens: Tokens

class AuthResponse(BaseModel):
    success: bool
    data: AuthData
