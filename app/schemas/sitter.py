from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import date, datetime
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
    phone: Optional[str] = None # Added phone
    emergency_contact_name: str
    emergency_contact_phone: str
    address: Optional[str] = None
    postal_code: Optional[str] = None # Added postal_code
    government_id_type: Optional[GovernmentIdType] = None
    government_id_number: Optional[str] = None
    government_id_image: Optional[str] = None

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
    is_boarding_supported: bool
    base_price: float
    boarding_max_pets: int
    boarding_overnight_supervision: bool
    boarding_allowed_pet_types: List[str]
    boarding_daily_walks: int
    boarding_potty_break_freq: PottyBreakFrequency
    boarding_sleeping_arrangement: SleepingArrangement
    boarding_separation_policy: bool

class SitterWalkingUpdate(BaseModel):
    is_dog_walking_supported: bool
    walking_duration: WalkDuration
    walking_type: WalkType
    walking_max_dogs: int
    walking_leash_type: LeashType
    walking_gps_tracking: bool
    walking_weather_policy: WeatherPolicy

class SitterHouseSittingUpdate(BaseModel):
    is_house_sitting_supported: bool
    house_sitting_overnight: bool
    house_sitting_daytime_hours: Optional[int] = None
    house_sitting_mail_collection: bool
    house_sitting_plant_watering: bool
    house_sitting_security_check: bool
    house_sitting_allowed_access: AllowedHomeAccess

class SitterDropInUpdate(BaseModel):
    is_drop_in_supported: bool
    drop_in_duration_min: int
    drop_in_visits_per_day: int
    drop_in_feeding: bool
    drop_in_litter_cleaning: bool
    drop_in_medication: bool
    drop_in_photo_update: bool

class SitterDayCareUpdate(BaseModel):
    is_day_care_supported: bool
    daycare_hours: Dict
    daycare_rest_periods: bool
    daycare_structured_play: bool
    daycare_size_separation: bool
    daycare_feeding_schedule: bool
    daycare_nap_area: bool

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

# --- Gallery Delete Schema ---
class SitterGalleryDelete(BaseModel):
    photos: List[str]

# --- Response Model ---
class SitterProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    onboarding_step: int
    background_check_status: BackgroundCheckStatus
    created_at: datetime
    
    # Personal Info
    date_of_birth: Optional[date]
    profile_photo: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    address: Optional[str]
    postal_code: Optional[str] = None # Added postal_code
    government_id_type: Optional[GovernmentIdType]
    government_id_number: Optional[str]
    government_id_image: Optional[str]
    id_verified: bool
    is_phone_verified: bool
    is_shahkar_verified: bool # Added
    
    # Location
    country: Optional[str]
    city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    service_radius_km: Optional[int]
    availability_type: Optional[AvailabilityType]
    available_days: List[str] = []
    available_time_slots: Dict = {}
    blackout_dates: List[date] = []
    
    # Experience
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
    
    # Home
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
    
    # Content
    headline: Optional[str]
    bio: Optional[str]
    care_routine_description: Optional[str]
    training_philosophy: Optional[str]
    photo_gallery: List[str] = []
    intro_video: Optional[str]
    
    # Pricing
    base_price: float
    additional_pet_price: float
    puppy_rate: float
    holiday_rate: float
    long_stay_discount: float
    cancellation_policy: Optional[CancellationPolicy]
    payout_method: Optional[PayoutMethod]
    payout_verified: bool

    # Supported Services Flags
    is_boarding_supported: bool
    is_house_sitting_supported: bool
    is_drop_in_supported: bool
    is_dog_walking_supported: bool
    is_day_care_supported: bool

    # Service-Specific Criteria (Boarding)
    boarding_max_pets: Optional[int]
    boarding_overnight_supervision: bool
    boarding_allowed_pet_types: List[str] = []
    boarding_daily_walks: Optional[int]
    boarding_potty_break_freq: Optional[PottyBreakFrequency]
    boarding_sleeping_arrangement: Optional[SleepingArrangement]
    boarding_separation_policy: bool

    # Service-Specific Criteria (House Sitting)
    house_sitting_overnight: bool
    house_sitting_daytime_hours: Optional[int]
    house_sitting_mail_collection: bool
    house_sitting_plant_watering: bool
    house_sitting_security_check: bool
    house_sitting_allowed_access: Optional[AllowedHomeAccess]

    # Service-Specific Criteria (Drop-In)
    drop_in_duration_min: Optional[int]
    drop_in_visits_per_day: Optional[int]
    drop_in_feeding: bool
    drop_in_litter_cleaning: bool
    drop_in_medication: bool
    drop_in_photo_update: bool

    # Service-Specific Criteria (Dog Walking)
    walking_duration: Optional[WalkDuration]
    walking_type: Optional[WalkType]
    walking_max_dogs: Optional[int]
    walking_leash_type: Optional[LeashType]
    walking_gps_tracking: bool
    walking_weather_policy: Optional[WeatherPolicy]

    # Service-Specific Criteria (Doggy Day Care)
    daycare_hours: Dict = {}
    daycare_rest_periods: bool
    daycare_structured_play: bool
    daycare_size_separation: bool
    daycare_feeding_schedule: bool
    daycare_nap_area: bool

    # Service-Specific Criteria (Dog Training)
    training_types: List[str] = []
    training_method: Optional[TrainingMethod]
    training_certifications: List[str] = []
    training_session_duration: Optional[int]
    training_packages: Dict = {}
    training_off_leash: bool
    training_behavioral_mod: bool
