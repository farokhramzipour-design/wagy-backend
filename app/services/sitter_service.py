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
from typing import List
import os

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

def update_personal_info(session: Session, user_id: UUID, data: SitterPersonalInfoUpdate):
    profile = get_or_create_profile(session, user_id)
    user = session.get(User, user_id)
    
    # Handle phone verification logic
    if data.phone and data.phone != user.phone_number:
        # If user is trying to update phone number
        # We should trigger OTP verification.
        # However, this function is a PATCH update. It expects the update to happen immediately.
        # If we need OTP, we can't update immediately.
        
        # Option 1: Return an error saying "Phone verification required" and trigger OTP.
        # But the frontend might expect a specific flow.
        
        # Let's assume the frontend calls a separate endpoint to verify the new phone first?
        # Or, we can send OTP here and return a status indicating OTP sent.
        
        # But the prompt says: "if he or she didnt login with phone number should verify his phone number using otp"
        
        # Let's implement this:
        # If phone is provided and different:
        # 1. Send OTP to the new phone.
        # 2. Do NOT update the phone in profile yet.
        # 3. Return a message or status code indicating OTP sent.
        
        # But this function returns SitterProfileResponse.
        # We might need to raise an HTTPException with a specific detail code that the frontend can handle.
        
        # Alternatively, we can just send the OTP and expect the user to call another endpoint to verify it.
        # Let's try to send OTP and raise an exception or return a special response.
        # Raising exception is cleaner for flow control if we want to stop the update.
        
        request_mobile_otp(data.phone)
        raise HTTPException(status_code=403, detail="Phone number verification required. OTP sent to the new number.")
        
    # If phone is same or not provided, proceed with update
    for key, value in data.dict(exclude_unset=True).items():
        if key == 'phone':
             continue # Skip phone update here, it should be updated via verification or if it matches user.phone_number
        setattr(profile, key, value)
    
    # If phone matches user.phone_number, we can sync it to profile
    if user.phone_number:
        profile.phone = user.phone_number

    update_step(profile, 2) # Completed Step 2
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def verify_profile_phone_update(session: Session, user_id: UUID, phone: str, otp: str):
    # Verify OTP
    # We can reuse verify_mobile_otp_login logic but we don't want to login, just verify.
    # verify_mobile_otp_login does login/registration.
    # We need a simple verify function.
    
    # Let's assume verify_mobile_otp_login verifies the OTP with the provider.
    # We can extract the verification part or call the provider directly.
    # Since verify_mobile_otp_login is coupled with login logic, let's duplicate the verification call here or refactor.
    # I'll use the request logic directly here for simplicity as I can't easily refactor auth_service without reading it again fully.
    # Actually I read it. verify_mobile_otp_login calls http_requests.put(MOBILE_OTP_URL, ...)
    
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
    user.phone_number = phone
    user.is_phone_verified = True
    session.add(user)
    
    profile = get_or_create_profile(session, user_id)
    profile.phone = phone
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
