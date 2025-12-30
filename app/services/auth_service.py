from sqlmodel import Session, select
from fastapi import HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings
from app.models.user import User, AuthProvider, AuthProviderEnum
from app.core.security import create_access_token, create_refresh_token
from app.schemas.auth import AuthResponse, AuthData, UserResponse, Tokens

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
