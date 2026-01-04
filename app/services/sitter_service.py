from uuid import UUID
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.sitter import SitterProfile
from app.models.user import User
from app.schemas.sitter import (
    SitterPersonalInfoUpdate, SitterLocationUpdate, SitterBoardingUpdate,
    SitterWalkingUpdate, SitterExperienceUpdate, SitterHomeUpdate,
    SitterContentUpdate, SitterPricingUpdate
)
from typing import List

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
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    update_step(profile, 2) # Completed Step 2
    
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
