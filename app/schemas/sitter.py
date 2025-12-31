from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import date
from uuid import UUID
from app.models.sitter import (
    GovernmentIdType, BackgroundCheckStatus, AvailabilityType, HomeType, HomeOwnership,
    YardSize, CancellationPolicy, PayoutMethod, PottyBreakFrequency, SleepingArrangement,
    AllowedHomeAccess, WalkDuration, WalkType, LeashType, WeatherPolicy, TrainingMethod
)

# --- Step 2: Personal Information ---
class SitterPersonalInfoUpdate(BaseModel):
    full_name: str
    date_of_birth: date
    profile_photo: Optional[str] = None # URL
    emergency_contact_name: str
    emergency_contact_phone: str

# --- Step 3: Location & Availability ---
class SitterLocationUpdate(BaseModel):
    country: str
    city: str
    latitude: float
    longitude: float
    service_radius_km: int
    availability_type: AvailabilityType
    available_days: List[str]
    available_time_slots: Dict
    blackout_dates: List[date]

# --- Step 5: Service-Specific Setup ---
class SitterBoardingUpdate(BaseModel):
    base_price: float
    boarding_max_pets: int
    boarding_overnight_supervision: bool
    boarding_allowed_pet_types: List[str]
    boarding_daily_walks: int
    boarding_potty_break_freq: PottyBreakFrequency
    boarding_sleeping_arrangement: SleepingArrangement
    boarding_separation_policy: bool

class SitterWalkingUpdate(BaseModel):
    walking_duration: WalkDuration
    walking_type: WalkType
    walking_max_dogs: int
    walking_leash_type: LeashType
    walking_gps_tracking: bool
    walking_weather_policy: WeatherPolicy

# --- Step 6: Experience & Skills ---
class SitterExperienceUpdate(BaseModel):
    years_of_experience: int
    pet_experience_types: List[str]
    breeds_experience: List[str]
    size_experience: List[str]
    puppy_experience: bool
    senior_pet_experience: bool
    medication_experience: bool
    behavioral_experience: List[str]
    first_aid_certified: bool
    vet_clinic_reference: Optional[str] = None

# --- Step 7: Home Environment ---
class SitterHomeUpdate(BaseModel):
    home_type: HomeType
    home_ownership: HomeOwnership
    fenced_yard: bool
    yard_size: YardSize
    pets_in_home: bool
    own_pets_details: Dict
    children_in_home: bool
    smoking_home: bool
    crate_available: bool
    cameras_in_home: bool

# --- Step 9: Profile Content ---
class SitterContentUpdate(BaseModel):
    headline: str
    bio: str
    care_routine_description: Optional[str] = None
    training_philosophy: Optional[str] = None
    photo_gallery: List[str]
    intro_video: Optional[str] = None

# --- Step 10: Pricing & Payouts ---
class SitterPricingUpdate(BaseModel):
    additional_pet_price: float
    puppy_rate: float
    holiday_rate: float
    long_stay_discount: float
    cancellation_policy: CancellationPolicy
    payout_method: PayoutMethod

# --- Response Model ---
class SitterProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: Optional[str]
    onboarding_step: int
    background_check_status: BackgroundCheckStatus
    created_at: date
    # Include other fields as needed for the frontend to repopulate forms
    date_of_birth: Optional[date]
    profile_photo: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    country: Optional[str]
    city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    service_radius_km: Optional[int]
    availability_type: Optional[AvailabilityType]
    available_days: List[str] = []
    available_time_slots: Dict = {}
    blackout_dates: List[date] = []
    years_of_experience: int
    pet_experience_types: List[str] = []
    breeds_experience: List[str] = []
    size_experience: List[str] = []
    puppy_experience: bool
    senior_pet_experience: bool
    medication_experience: bool
    behavioral_experience: List[str] = []
    first_aid_certified: bool
    vet_clinic_reference: Optional[str]
    home_type: Optional[HomeType]
    home_ownership: Optional[HomeOwnership]
    fenced_yard: bool
    yard_size: Optional[YardSize]
    pets_in_home: bool
    own_pets_details: Dict = {}
    children_in_home: bool
    smoking_home: bool
    crate_available: bool
    cameras_in_home: bool
    headline: Optional[str]
    bio: Optional[str]
    care_routine_description: Optional[str]
    training_philosophy: Optional[str]
    photo_gallery: List[str] = []
    intro_video: Optional[str]
    base_price: float
    additional_pet_price: float
    puppy_rate: float
    holiday_rate: float
    long_stay_discount: float
    cancellation_policy: Optional[CancellationPolicy]
    payout_method: Optional[PayoutMethod]
    payout_verified: bool
