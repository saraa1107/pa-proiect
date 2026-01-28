from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable pentru utilizatori vechi
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relații (terapeuți au copii)
    children = relationship("Child", back_populates="therapist", cascade="all, delete-orphan")


class Child(Base):
    """Profil copil creat de terapeut. Fiecare copil are tabla AAC proprie."""
    __tablename__ = "children"
    __table_args__ = (
        UniqueConstraint('name', 'therapist_id', name='uq_child_name_therapist'),
    )

    id = Column(Integer, primary_key=True, index=True)
    therapist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    therapist = relationship("User", back_populates="children")
    categories = relationship("Category", back_populates="child", cascade="all, delete-orphan")
    symbols = relationship("Symbol", back_populates="child", cascade="all, delete-orphan")
    favorite_symbols = relationship("FavoriteSymbol", back_populates="child", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint('name', 'child_id', name='uq_category_name_child'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(255), nullable=True)  # URL sau path către iconiță
    color = Column(String(7), nullable=True)  # Hex color code
    child_id = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=True)  # null = global
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relații
    child = relationship("Child", back_populates="categories")
    symbols = relationship("Symbol", back_populates="category", cascade="all, delete-orphan")


class Symbol(Base):
    __tablename__ = "symbols"
    __table_args__ = (
        UniqueConstraint('name', 'category_id', 'child_id', name='uq_symbol_name_category_child'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    text = Column(String(255), nullable=False)  # Textul care va fi vorbit
    image_url = Column(String(500), nullable=False)  # URL sau path către imagine
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    child_id = Column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=True)  # null = global
    display_order = Column(Integer, default=0)  # Pentru reordonare în mod terapeut
    usage_count = Column(Integer, default=0)  # Contor pentru utilizări
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relații
    category = relationship("Category", back_populates="symbols")
    child = relationship("Child", back_populates="symbols")
    favorites = relationship("FavoriteSymbol", back_populates="symbol")


class FavoriteSymbol(Base):
    """Simboluri favorite per copil (mod terapeut)."""
    __tablename__ = "favorite_symbols"
    __table_args__ = (
        UniqueConstraint('child_id', 'symbol_id', name='uq_favorite_child_symbol'),
    )

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    child = relationship("Child", back_populates="favorite_symbols")
    symbol = relationship("Symbol", back_populates="favorites")


