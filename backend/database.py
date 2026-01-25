from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Creează directorul pentru baza de date dacă nu există
os.makedirs("data", exist_ok=True)

# URL-ul bazei de date SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/aac_database.db"

# Creează engine-ul SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Necesar pentru SQLite
)

# Creează SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creează Base class pentru modele
Base = declarative_base()


