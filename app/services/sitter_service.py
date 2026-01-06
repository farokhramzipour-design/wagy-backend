from uuid import UUID
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.sitter import SitterProfile
from app.models.user import User
from app.schemas.sitter import (
    SitterPersonalInfoUpdate, SitterLocationUpdate, SitterBoardingUpdate,
    SitterWalkingUpdate, SitterExperienceUpdate, SitterHomeUpdate,
    SitterContentUpdate, SitterPricingUpdate, SitterGalleryDelete
)
from app.services.auth_service import request_mobile_otp, verify_mobile_otp_login
from app.services.verification_service import verify_shahkar
from typing import List
import os
import logging
import traceback

logger = logging.getLogger(__name__)

def get_or_create_profile(session: Session, user_id: UUID) -> SitterProfile:
    statement = select(SitterProfile).where(SitterProfile.user_id == user_id)
    profile = session.exec(statement).first()
    if not profile:
        # Get user to pre-fill name/phone if available
        user = session.get(User, user_id)
        profile = SitterProfile(
            user_id=user_id,
            full_name=user.full_name or "",
            phone=user.phone_number or "",
            email=user.email,
            profile_photo=user.avatar_url,
            date_of_birth=user.created_at.date(), # Placeholder, needs update
            onboarding_step=1 # Start at step 1
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)
    return profile

def update_step(profile: SitterProfile, step: int):
    # Only update if the new step is greater than the current step
    # This allows users to go back without resetting their progress indicator
    if step > profile.onboarding_step:
        profile.onboarding_step = step

async def update_personal_info(session: Session, user_id: UUID, data: SitterPersonalInfoUpdate):
    try:
        logger.info(f"Updating personal info for user {user_id}")
        profile = get_or_create_profile(session, user_id)
        user = session.get(User, user_id)
        
        # Determine phone number to use for verification
        phone_to_verify = data.phone if data.phone else (profile.phone or user.phone_number)
        
        # Shahkar Verification if government_id_number is provided
        if data.government_id_number:
            logger.info(f"Verifying Shahkar for phone {phone_to_verify} and ID {data.government_id_number}")
            if not phone_to_verify:
                 raise HTTPException(status_code=400, detail="Phone number is required for identity verification")
                 
            try:
                shahkar_response = await verify_shahkar(phone_to_verify, data.government_id_number)
                logger.info(f"Shahkar response: {shahkar_response}")
                # Check if matched is true
                # Response structure: {"response_body": {"data": {"matched": true}, ...}, "result": 1}
                matched = False
                if shahkar_response.get("result") == 1:
                    data_body = shahkar_response.get("response_body", {}).get("data", {})
                    if data_body and data_body.get("matched") is True:
                        matched = True
                
                if matched:
                    profile.is_shahkar_verified = True
                else:
                    raise HTTPException(status_code=400, detail="Phone number and national ID do not match")
                    
            except HTTPException as e:
                logger.error(f"Shahkar verification HTTP error: {e.detail}")
                raise e
            except Exception as e:
                logger.error(f"Shahkar verification failed: {e}")
                raise HTTPException(status_code=500, detail=f"Identity verification failed: {str(e)}")

        # Handle phone verification logic (OTP)
        if data.phone and data.phone != user.phone_number:
            logger.info(f"Phone number change detected. Requesting OTP for {data.phone}")
            request_mobile_otp(data.phone)
            raise HTTPException(status_code=403, detail="Phone number verification required. OTP sent to the new number.")
            
        # If phone is same or not provided, proceed with update
        for key, value in data.dict(exclude_unset=True).items():
            if key == 'phone':
                 continue # Skip phone update here
            setattr(profile, key, value)
        
        # If phone matches user.phone_number, we can sync it to profile
        if user.phone_number:
            profile.phone = user.phone_number
            profile.is_phone_verified = True

        update_step(profile, 2) # Completed Step 2
        
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile
    except Exception as e:
        logger.error(f"Error in update_personal_info: {e}")
        traceback.print_exc()
        raise e

def verify_profile_phone_update(session: Session, user_id: UUID, phone: str, otp: str):
    import requests as http_requests
    MOBILE_OTP_URL = "https://api-staging.hyperlikes.ir/public/core/apiv1/custom_codes"
    
    payload = {'phoneNumber': phone, 'code': otp}
    try:
        response = http_requests.put(MOBILE_OTP_URL, data=payload)
        if response.status_code != 200:
             raise HTTPException(status_code=400, detail="Invalid OTP")
    except http_requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to verify OTP: {str(e)}")
        
    # OTP Verified. Update User and Profile.
    user = session.get(User, user_id)
    
    # Check if phone number is already taken by another user
    existing_user_statement = select(User).where(User.phone_number == phone)
    existing_user = session.exec(existing_user_statement).first()
    
    if existing_user and existing_user.id != user_id:
        raise HTTPException(status_code=400, detail="Phone number already in use by another account")

    user.phone_number = phone
    user.is_phone_verified = True
    session.add(user)
    
    profile = get_or_create_profile(session, user_id)
    profile.phone = phone
    profile.is_phone_verified = True
    session.add(profile)
    
    session.commit()
    session.refresh(profile)
    return profile

def update_profile_photo(session: Session, user_id: UUID, photo_path: str):
    profile = get_or_create_profile(session, user_id)
    profile.profile_photo = photo_path
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def update_government_id_image(session: Session, user_id: UUID, photo_path: str):
    profile = get_or_create_profile(session, user_id)
    profile.government_id_image = photo_path
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def add_gallery_photos(session: Session, user_id: UUID, photo_paths: List[str]):
    profile = get_or_create_profile(session, user_id)
    
    # Ensure photo_gallery is a list
    current_gallery = list(profile.photo_gallery) if profile.photo_gallery else []
    
    if len(current_gallery) + len(photo_paths) > 10:
        raise HTTPException(status_code=400, detail="Gallery cannot exceed 10 photos")
        
    profile.photo_gallery = current_gallery + photo_paths
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def delete_gallery_photos(session: Session, user_id: UUID, data: SitterGalleryDelete):
    profile = get_or_create_profile(session, user_id)
    current_gallery = list(profile.photo_gallery) if profile.photo_gallery else []
    
    # Filter out photos to be deleted
    # We need to handle both full URLs and relative paths if the frontend sends full URLs
    # Assuming the frontend sends the exact string it received
    
    # Helper to extract relative path if it's a full URL
    def get_relative_path(path_or_url: str) -> str:
        if "uploads/gallery_photos/" in path_or_url:
            return "uploads/gallery_photos/" + path_or_url.split("uploads/gallery_photos/")[-1]
        return path_or_url

    photos_to_delete_relative = [get_relative_path(p) for p in data.photos]
    
    new_gallery = []
    for photo in current_gallery:
        if photo not in photos_to_delete_relative:
            new_gallery.append(photo)
        else:
            # Delete file from disk
            if os.path.exists(photo):
                try:
                    os.remove(photo)
                except OSError:
                    pass # Log error or ignore if file doesn't exist
                    
    profile.photo_gallery = new_gallery
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def update_location(session: Session, user_id: UUID, data: SitterLocationUpdate):
    profile = get_or_create_profile(session, user_id)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    update_step(profile, 3) # Completed Step 3
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def update_boarding_service(session: Session, user_id: UUID, data: SitterBoardingUpdate):
    profile = get_or_create_profile(session, user_id)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    update_step(profile, 5) # Completed Step 5 (Services)
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def update_walking_service(session: Session, user_id: UUID, data: SitterWalkingUpdate):
    profile = get_or_create_profile(session, user_id)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    update_step(profile, 5) # Completed Step 5 (Services)
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def update_experience(session: Session, user_id: UUID, data: SitterExperienceUpdate):
    profile = get_or_create_profile(session, user_id)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    update_step(profile, 6) # Completed Step 6
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def update_home(session: Session, user_id: UUID, data: SitterHomeUpdate):
    profile = get_or_create_profile(session, user_id)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    update_step(profile, 7) # Completed Step 7
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def update_content(session: Session, user_id: UUID, data: SitterContentUpdate):
    profile = get_or_create_profile(session, user_id)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    update_step(profile, 9) # Completed Step 9
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def update_pricing(session: Session, user_id: UUID, data: SitterPricingUpdate):
    profile = get_or_create_profile(session, user_id)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    update_step(profile, 10) # Completed Step 10

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def get_profile(session: Session, user_id: UUID):
    statement = select(SitterProfile).where(SitterProfile.user_id == user_id)
    profile = session.exec(statement).first()
    if not profile:
        # Create empty profile if not exists, so frontend can start onboarding
        return get_or_create_profile(session, user_id)
    return profile
