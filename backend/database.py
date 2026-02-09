from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

try:
    from decouple import config
except ImportError:
    # Fallback dacă decouple nu e instalat (pentru dev local)
    def config(key, default=None):
        return os.getenv(key, default)

# Creează directorul pentru baza de date dacă nu există (pentru SQLite)
os.makedirs("data", exist_ok=True)

# Citește DATABASE_URL din environment (production) sau folosește SQLite (development)
DATABASE_URL = config('DATABASE_URL', default='sqlite:///./data/aac_database.db')

# Fix pentru Render PostgreSQL (folosește postgresql:// nu postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"🔗 Database: {DATABASE_URL.split('@')[0]}...")

# Creează engine-ul SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    # PostgreSQL (production)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verifică conexiunea înainte de fiecare query
        pool_recycle=3600,   # Recrează conexiuni după 1h
    )
    print("✅ PostgreSQL engine configured")
else:
    # SQLite (development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # Necesar pentru SQLite
    )
    print("✅ SQLite engine configured")

# Creează SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creează Base class pentru modele
Base = declarative_base()


