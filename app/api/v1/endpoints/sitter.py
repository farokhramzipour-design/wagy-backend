from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from sqlmodel import Session
from app.db.session import get_session
from app.core.security import get_current_user_token
from app.core.config import settings
from jose import jwt
from uuid import UUID, uuid4
from app.schemas.sitter import (
    SitterPersonalInfoUpdate, SitterLocationUpdate, SitterBoardingUpdate,
    SitterWalkingUpdate, SitterExperienceUpdate, SitterHomeUpdate,
    SitterContentUpdate, SitterPricingUpdate, SitterProfileResponse,
    SitterGalleryDelete
)
from app.services import sitter_service
import shutil
import os
from typing import List

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

def get_full_url(request: Request, path: str) -> str:
    if not path:
        return path
    if path.startswith("http"):
        return path
    base_url = str(request.base_url).rstrip("/")
    # Ensure path doesn't start with / if base_url ends with / (though rstrip handles that)
    # But path might be relative like "uploads/..."
    if not path.startswith("/"):
        path = "/" + path
    return f"{base_url}{path}"

@router.get("/me", response_model=SitterProfileResponse)
async def get_my_profile(
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    profile = sitter_service.get_profile(session, user_id)
    if profile.profile_photo:
         profile.profile_photo = get_full_url(request, profile.profile_photo)
    
    if profile.photo_gallery:
        profile.photo_gallery = [get_full_url(request, p) for p in profile.photo_gallery]
        
    return profile

@router.patch("/personal-info", response_model=SitterProfileResponse)
async def update_personal_info(
    data: SitterPersonalInfoUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return sitter_service.update_personal_info(session, user_id, data)

@router.post("/upload-profile-photo", response_model=SitterProfileResponse)
async def upload_profile_photo(
    request: Request,
    file: UploadFile = File(...),
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    # Ensure upload directory exists
    upload_dir = "uploads/profile_photos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Clean up previous photos for this user
    for filename in os.listdir(upload_dir):
        if filename.startswith(str(user_id)):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    # Generate file path
    _, file_extension = os.path.splitext(file.filename)
    if not file_extension:
        file_extension = ".jpg"
        
    file_name = f"{user_id}{file_extension}"
    file_path = f"{upload_dir}/{file_name}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update profile with file path
    profile = sitter_service.update_profile_photo(session, user_id, file_path)
    
    # Return full URL in response
    if profile.profile_photo:
         profile.profile_photo = get_full_url(request, profile.profile_photo)
         
    return profile

@router.post("/upload-gallery-photos", response_model=SitterProfileResponse)
async def upload_gallery_photos(
    request: Request,
    files: List[UploadFile] = File(...),
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    # Ensure upload directory exists
    upload_dir = "uploads/gallery_photos"
    os.makedirs(upload_dir, exist_ok=True)
    
    saved_paths = []
    
    for file in files:
        # Generate unique file name
        _, file_extension = os.path.splitext(file.filename)
        if not file_extension:
            file_extension = ".jpg"
            
        file_name = f"{user_id}_{uuid4()}{file_extension}"
        file_path = f"{upload_dir}/{file_name}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        saved_paths.append(file_path)
        
    # Update profile with file paths
    try:
        profile = sitter_service.add_gallery_photos(session, user_id, saved_paths)
    except HTTPException as e:
        # If error (e.g. too many photos), clean up uploaded files
        for path in saved_paths:
            if os.path.exists(path):
                os.remove(path)
        raise e
    
    # Return full URLs
    if profile.photo_gallery:
        profile.photo_gallery = [get_full_url(request, p) for p in profile.photo_gallery]
        
    return profile

@router.post("/delete-gallery-photos", response_model=SitterProfileResponse)
async def delete_gallery_photos(
    request: Request,
    data: SitterGalleryDelete,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    profile = sitter_service.delete_gallery_photos(session, user_id, data)
    
    # Return full URLs
    if profile.photo_gallery:
        profile.photo_gallery = [get_full_url(request, p) for p in profile.photo_gallery]

    return profile

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
