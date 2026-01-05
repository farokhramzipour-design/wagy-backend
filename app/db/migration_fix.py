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
            conn.commit()
            logger.info("Migration fix completed successfully.")
    except Exception as e:
        logger.error(f"Migration fix failed: {e}")
