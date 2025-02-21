from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.models import Base, Obituary
import app.core.config as config

# Create a database engine
engine = create_engine(config.DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to create tables if they don’t exist
def init_db():
    Base.metadata.create_all(bind=engine)

# Function to get a new database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
