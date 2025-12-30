from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class GoogleAuthRequest(BaseModel):
    id_token: str

class EmailLoginRequest(BaseModel):
    email: EmailStr

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str

class MobileLoginRequest(BaseModel):
    phone_number: str

class VerifyMobileOtpRequest(BaseModel):
    phone_number: str
    otp: str

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
