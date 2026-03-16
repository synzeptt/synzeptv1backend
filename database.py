"""Database configuration and initialization for Synzept."""

from sqlalchemy.orm import declarative_base

Base = declarative_base()


def init_database():
    """Initialize the database by creating all tables."""
    # Import models to ensure they are registered with Base
    from models import User, UserProfile, Conversation, Memory, Idea, Goal, Project
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_database()