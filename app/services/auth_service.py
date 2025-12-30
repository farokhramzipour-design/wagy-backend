import random
import string
import requests as http_requests
from datetime import datetime, timedelta
from sqlmodel import Session, select
from fastapi import HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings
from app.models.user import User, AuthProvider, AuthProviderEnum
from app.core.security import create_access_token, create_refresh_token
from app.schemas.auth import AuthResponse, AuthData, UserResponse, Tokens
from app.services.email_service import send_otp_email

# In-memory OTP storage (For production, use Redis)
otp_storage = {}

# In-memory Token Blacklist (For production, use Redis)
token_blacklist = set()

MOBILE_OTP_URL = "https://api-staging.hyperlikes.ir/public/core/apiv1/custom_codes"

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

async def request_otp(session: Session, email: str):
    otp = generate_otp()
    # Store OTP with expiration (e.g., 5 minutes)
    otp_storage[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    }
    
    # Send email
    await send_otp_email(email, otp)
    return {"message": "OTP sent successfully"}

def verify_otp_login(session: Session, email: str, otp: str) -> AuthResponse:
    stored_data = otp_storage.get(email)
    
    if not stored_data:
        raise HTTPException(status_code=400, detail="OTP not requested or expired")
    
    if datetime.utcnow() > stored_data["expires_at"]:
        del otp_storage[email]
        raise HTTPException(status_code=400, detail="OTP expired")
        
    if stored_data["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # OTP Verified. Clear it.
    del otp_storage[email]
    
    # Check if user exists
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    
    if not user:
        # Register new user
        user = User(
            email=email,
            is_email_verified=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Add Email Auth Provider (optional, since email is on user record, but good for consistency)
        auth_provider = AuthProvider(
            user_id=user.id,
            provider=AuthProviderEnum.EMAIL,
            provider_uid=email
        )
        session.add(auth_provider)
        session.commit()
    
    return create_auth_response(user)

def request_mobile_otp(phone_number: str):
    payload = {'phoneNumber': phone_number}
    try:
        response = http_requests.post(MOBILE_OTP_URL, data=payload)
        response.raise_for_status()
        return {"message": "OTP sent successfully"}
    except http_requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to send OTP: {str(e)}")

def verify_mobile_otp_login(session: Session, phone_number: str, otp: str) -> AuthResponse:
    payload = {'phoneNumber': phone_number, 'code': otp}
    try:
        response = http_requests.put(MOBILE_OTP_URL, data=payload)
        if response.status_code != 200:
             raise HTTPException(status_code=400, detail="Invalid OTP")
    except http_requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to verify OTP: {str(e)}")

    # Check if user exists by phone number
    statement = select(User).where(User.phone_number == phone_number)
    user = session.exec(statement).first()
    
    if not user:
        # Register new user
        user = User(
            phone_number=phone_number,
            is_phone_verified=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Add OTP Auth Provider
        auth_provider = AuthProvider(
            user_id=user.id,
            provider=AuthProviderEnum.OTP,
            provider_uid=phone_number
        )
        session.add(auth_provider)
        session.commit()
    
    return create_auth_response(user)

def verify_google_token(token: str):
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
        return id_info
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")

def create_auth_response(user: User) -> AuthResponse:
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }
    
    access_token = create_access_token(data=token_payload)
    refresh_token = create_refresh_token(data=token_payload)
    
    return AuthResponse(
        success=True,
        data=AuthData(
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                is_email_verified=user.is_email_verified
            ),
            tokens=Tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
    )

def authenticate_google_user(session: Session, token: str) -> AuthResponse:
    id_info = verify_google_token(token)
    
    google_user_id = id_info['sub']
    email = id_info.get('email')
    name = id_info.get('name')
    picture = id_info.get('picture')

    # 1. Check if auth_provider exists
    statement = select(AuthProvider).where(
        AuthProvider.provider == AuthProviderEnum.GOOGLE,
        AuthProvider.provider_uid == google_user_id
    )
    existing_auth_provider = session.exec(statement).first()

    if existing_auth_provider:
        user = session.get(User, existing_auth_provider.user_id)
        return create_auth_response(user)

    # 2. Check if user exists by email (Link account)
    statement = select(User).where(User.email == email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        new_auth_provider = AuthProvider(
            user_id=existing_user.id,
            provider=AuthProviderEnum.GOOGLE,
            provider_uid=google_user_id
        )
        session.add(new_auth_provider)
        session.commit()
        
        return create_auth_response(existing_user)

    # 3. Register new user
    new_user = User(
        email=email,
        full_name=name,
        avatar_url=picture,
        is_email_verified=True
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    new_auth_provider = AuthProvider(
        user_id=new_user.id,
        provider=AuthProviderEnum.GOOGLE,
        provider_uid=google_user_id
    )
    session.add(new_auth_provider)
    session.commit()
    
    return create_auth_response(new_user)

def logout_user(token: str):
    token_blacklist.add(token)
    return {"message": "Successfully logged out"}
