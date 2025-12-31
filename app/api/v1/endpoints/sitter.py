from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.core.security import get_current_user_token
from app.core.config import settings
from jose import jwt
from uuid import UUID
from app.schemas.sitter import (
    SitterPersonalInfoUpdate, SitterLocationUpdate, SitterBoardingUpdate,
    SitterWalkingUpdate, SitterExperienceUpdate, SitterHomeUpdate,
    SitterContentUpdate, SitterPricingUpdate, SitterProfileResponse
)
from app.services import sitter_service
import shutil
import os

router = APIRouter()

def get_current_user_id(token: str = Depends(get_current_user_token)) -> UUID:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UUID(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me", response_model=SitterProfileResponse)
async def get_my_profile(
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return sitter_service.get_profile(session, user_id)

@router.patch("/personal-info", response_model=SitterProfileResponse)
async def update_personal_info(
    data: SitterPersonalInfoUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return sitter_service.update_personal_info(session, user_id, data)

@router.post("/upload-profile-photo", response_model=SitterProfileResponse)
async def upload_profile_photo(
    file: UploadFile = File(...),
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    # Ensure upload directory exists
    upload_dir = "uploads/profile_photos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Clean up previous photos for this user
    # Remove any existing file that starts with the user_id to avoid duplicates (e.g. .jpg vs .png)
    for filename in os.listdir(upload_dir):
        if filename.startswith(str(user_id)):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    # Generate file path
    # Use os.path.splitext to safely get extension
    _, file_extension = os.path.splitext(file.filename)
    if not file_extension:
        file_extension = ".jpg" # Default fallback
        
    file_name = f"{user_id}{file_extension}"
    file_path = f"{upload_dir}/{file_name}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update profile with file path
    return sitter_service.update_profile_photo(session, user_id, file_path)

@router.patch("/location", response_model=SitterProfileResponse)
async def update_location(
    data: SitterLocationUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return sitter_service.update_location(session, user_id, data)

@router.patch("/services/boarding", response_model=SitterProfileResponse)
async def update_boarding(
    data: SitterBoardingUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return sitter_service.update_boarding_service(session, user_id, data)

@router.patch("/services/walking", response_model=SitterProfileResponse)
async def update_walking(
    data: SitterWalkingUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return sitter_service.update_walking_service(session, user_id, data)

@router.patch("/experience", response_model=SitterProfileResponse)
async def update_experience(
    data: SitterExperienceUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return sitter_service.update_experience(session, user_id, data)

@router.patch("/home", response_model=SitterProfileResponse)
async def update_home(
    data: SitterHomeUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return sitter_service.update_home(session, user_id, data)

@router.patch("/content", response_model=SitterProfileResponse)
async def update_content(
    data: SitterContentUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return sitter_service.update_content(session, user_id, data)

@router.patch("/pricing", response_model=SitterProfileResponse)
async def update_pricing(
    data: SitterPricingUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return sitter_service.update_pricing(session, user_id, data)
