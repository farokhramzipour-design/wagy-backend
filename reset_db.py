from sqlmodel import SQLModel
from app.db.session import engine
# Import all models to ensure they are registered with SQLModel.metadata
from app.models.user import User, AuthProvider
from app.models.sitter import SitterProfile

def reset_database():
    print("Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    print("Creating all tables...")
    SQLModel.metadata.create_all(engine)
    print("Database reset complete.")

if __name__ == "__main__":
    reset_database()
