import uuid
from datetime import date, datetime
from typing import Optional, List, Dict
from enum import Enum as PyEnum
from sqlmodel import Field, SQLModel, Relationship, Column, JSON, ARRAY, String, Float, Date, Boolean, Integer, Text
from app.models.user import User

# Enums
class GovernmentIdType(str, PyEnum):
    PASSPORT = "passport"
    NATIONAL_ID = "national_id"

class BackgroundCheckStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AvailabilityType(str, PyEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"

class HomeType(str, PyEnum):
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    FARM = "farm"

class HomeOwnership(str, PyEnum):
    OWN = "own"
    RENT = "rent"

class YardSize(str, PyEnum):
    NONE = "none"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class CancellationPolicy(str, PyEnum):
    FLEXIBLE = "flexible"
    MODERATE = "moderate"
    STRICT = "strict"

class PayoutMethod(str, PyEnum):
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"

class PottyBreakFrequency(str, PyEnum):
    EVERY_HOUR = "every_hour"
    EVERY_2_HOURS = "every_2_hours"
    EVERY_4_HOURS = "every_4_hours"
    EVERY_8_HOURS = "every_8_hours"

class SleepingArrangement(str, PyEnum):
    IN_BED = "in_bed"
    IN_CRATE = "in_crate"
    IN_OWN_BED = "in_own_bed"
    ANYWHERE = "anywhere"

class AllowedHomeAccess(str, PyEnum):
    FULL_ACCESS = "full_access"
    LIMITED_ACCESS = "limited_access"

class WalkDuration(str, PyEnum):
    MIN_30 = "30_min"
    MIN_60 = "60_min"

class WalkType(str, PyEnum):
    PRIVATE = "private"
    GROUP = "group"

class LeashType(str, PyEnum):
    STANDARD = "standard"
    RETRACTABLE = "retractable"
    LONG_LINE = "long_line"

class WeatherPolicy(str, PyEnum):
    RAIN_OR_SHINE = "rain_or_shine"
    NO_EXTREME_WEATHER = "no_extreme_weather"

class TrainingMethod(str, PyEnum):
    POSITIVE_REINFORCEMENT = "positive_reinforcement"
    BALANCED = "balanced"
    OTHER = "other"

# Main Sitter Profile
class SitterProfile(SQLModel, table=True):
    __tablename__ = "sitter_profiles"
    
    # Identity & Verification
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True)
    full_name: str
    profile_photo: Optional[str] = None
    date_of_birth: date
    phone: str
    email: Optional[str] = None
    government_id_type: Optional[GovernmentIdType] = None
    government_id_number: Optional[str] = None
    government_id_image: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    id_verified: bool = Field(default=False)
    is_phone_verified: bool = Field(default=False)
    is_shahkar_verified: bool = Field(default=False)
    background_check_status: BackgroundCheckStatus = Field(default=BackgroundCheckStatus.PENDING)
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    # Onboarding Completion Flags
    is_personal_info_completed: bool = Field(default=False)
    is_location_completed: bool = Field(default=False)
    is_services_selected: bool = Field(default=False)
    is_boarding_completed: bool = Field(default=False)
    is_house_sitting_completed: bool = Field(default=False)
    is_drop_in_completed: bool = Field(default=False)
    is_dog_walking_completed: bool = Field(default=False)
    is_day_care_completed: bool = Field(default=False)
    is_experience_completed: bool = Field(default=False)
    is_home_completed: bool = Field(default=False)
    is_content_completed: bool = Field(default=False)
    is_pricing_completed: bool = Field(default=False)

    # Location & Availability
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    service_radius_km: Optional[int] = None
    availability_type: Optional[AvailabilityType] = None
    available_days: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    available_time_slots: Dict = Field(default={}, sa_column=Column(JSON))
    blackout_dates: List[date] = Field(default=[], sa_column=Column(ARRAY(Date)))

    # Experience & Skills
    years_of_experience: int = Field(default=0)
    pet_experience_types: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    breeds_experience: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    size_experience: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    puppy_experience: bool = Field(default=False)
    senior_pet_experience: bool = Field(default=False)
    medication_experience: bool = Field(default=False)
    behavioral_experience: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    first_aid_certified: bool = Field(default=False)
    vet_clinic_reference: Optional[str] = None

    # Home Environment
    home_type: Optional[HomeType] = None
    home_ownership: Optional[HomeOwnership] = None
    fenced_yard: bool = Field(default=False)
    yard_size: Optional[YardSize] = None
    pets_in_home: bool = Field(default=False)
    own_pets_details: Dict = Field(default={}, sa_column=Column(JSON))
    children_in_home: bool = Field(default=False)
    smoking_home: bool = Field(default=False)
    crate_available: bool = Field(default=False)
    cameras_in_home: bool = Field(default=False)

    # Pricing & Payments
    base_price: float = Field(default=0.0)
    additional_pet_price: float = Field(default=0.0)
    puppy_rate: float = Field(default=0.0)
    holiday_rate: float = Field(default=0.0)
    long_stay_discount: float = Field(default=0.0) # Percentage
    cancellation_policy: Optional[CancellationPolicy] = None
    payout_method: Optional[PayoutMethod] = None
    payout_verified: bool = Field(default=False)

    # Profile Content
    headline: Optional[str] = None
    bio: Optional[str] = Field(default=None, sa_column=Column(Text))
    care_routine_description: Optional[str] = Field(default=None, sa_column=Column(Text))
    training_philosophy: Optional[str] = Field(default=None, sa_column=Column(Text))
    photo_gallery: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    intro_video: Optional[str] = None

    # Supported Services Flags
    is_boarding_supported: bool = Field(default=False)
    is_house_sitting_supported: bool = Field(default=False)
    is_drop_in_supported: bool = Field(default=False)
    is_dog_walking_supported: bool = Field(default=False)
    is_day_care_supported: bool = Field(default=False)

    # Service-Specific Criteria (Boarding)
    boarding_max_pets: Optional[int] = None
    boarding_overnight_supervision: bool = Field(default=False)
    boarding_allowed_pet_types: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    boarding_daily_walks: Optional[int] = None
    boarding_potty_break_freq: Optional[PottyBreakFrequency] = None
    boarding_sleeping_arrangement: Optional[SleepingArrangement] = None
    boarding_separation_policy: bool = Field(default=False)

    # Service-Specific Criteria (House Sitting)
    house_sitting_overnight: bool = Field(default=False)
    house_sitting_daytime_hours: Optional[int] = None
    house_sitting_mail_collection: bool = Field(default=False)
    house_sitting_plant_watering: bool = Field(default=False)
    house_sitting_security_check: bool = Field(default=False)
    house_sitting_allowed_access: Optional[AllowedHomeAccess] = None

    # Service-Specific Criteria (Drop-In)
    drop_in_duration_min: Optional[int] = None
    drop_in_visits_per_day: Optional[int] = None
    drop_in_feeding: bool = Field(default=False)
    drop_in_litter_cleaning: bool = Field(default=False)
    drop_in_medication: bool = Field(default=False)
    drop_in_photo_update: bool = Field(default=False)

    # Service-Specific Criteria (Dog Walking)
    walking_duration: Optional[WalkDuration] = None
    walking_type: Optional[WalkType] = None
    walking_max_dogs: Optional[int] = None
    walking_leash_type: Optional[LeashType] = None
    walking_gps_tracking: bool = Field(default=False)
    walking_weather_policy: Optional[WeatherPolicy] = None

    # Service-Specific Criteria (Doggy Day Care)
    daycare_hours: Dict = Field(default={}, sa_column=Column(JSON))
    daycare_rest_periods: bool = Field(default=False)
    daycare_structured_play: bool = Field(default=False)
    daycare_size_separation: bool = Field(default=False)
    daycare_feeding_schedule: bool = Field(default=False)
    daycare_nap_area: bool = Field(default=False)

    # Service-Specific Criteria (Dog Training)
    training_types: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    training_method: Optional[TrainingMethod] = None
    training_certifications: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    training_session_duration: Optional[int] = None
    training_packages: Dict = Field(default={}, sa_column=Column(JSON))
    training_off_leash: bool = Field(default=False)
    training_behavioral_mod: bool = Field(default=False)

    # Trust & Quality Signals
    rating: float = Field(default=0.0)
    completed_bookings: int = Field(default=0)
    repeat_clients: int = Field(default=0)
    reviews: Dict = Field(default={}, sa_column=Column(JSON))
    response_time_minutes: Optional[int] = None
    cancellation_rate: float = Field(default=0.0)

    # Mandatory Safety & Legal
    insurance_status: bool = Field(default=False)
    liability_acceptance: bool = Field(default=False)
    pet_emergency_protocol: Optional[str] = Field(default=None, sa_column=Column(Text))
    terms_accepted: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="sitter_profile")
