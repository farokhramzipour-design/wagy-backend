from sqlmodel import text
from app.db.session import engine
import logging

logger = logging.getLogger(__name__)

def run_fix():
    try:
        with engine.connect() as conn:
            logger.info("Running migration fix...")
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS government_id_number VARCHAR;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS government_id_image VARCHAR;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS address VARCHAR;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS postal_code VARCHAR;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_phone_verified BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_shahkar_verified BOOLEAN DEFAULT FALSE;"))
            
            # Add supported services flags
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_boarding_supported BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_house_sitting_supported BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_drop_in_supported BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_dog_walking_supported BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_day_care_supported BOOLEAN DEFAULT FALSE;"))

            # Add completion flags
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_personal_info_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_location_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_services_selected BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_boarding_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_house_sitting_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_drop_in_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_dog_walking_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_day_care_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_experience_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_home_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_content_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE sitter_profiles ADD COLUMN IF NOT EXISTS is_pricing_completed BOOLEAN DEFAULT FALSE;"))

            conn.commit()
            logger.info("Migration fix completed successfully.")
    except Exception as e:
        logger.error(f"Migration fix failed: {e}")
