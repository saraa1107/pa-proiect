from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relații
    favorite_symbols = relationship("FavoriteSymbol", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(255), nullable=True)  # URL sau path către iconiță
    color = Column(String(7), nullable=True)  # Hex color code
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relații
    symbols = relationship("Symbol", back_populates="category", cascade="all, delete-orphan")


class Symbol(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    text = Column(String(255), nullable=False)  # Textul care va fi vorbit
    image_url = Column(String(500), nullable=False)  # URL sau path către imagine
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    usage_count = Column(Integer, default=0)  # Contor pentru utilizări
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relații
    category = relationship("Category", back_populates="symbols")
    favorites = relationship("FavoriteSymbol", back_populates="symbol")


class FavoriteSymbol(Base):
    __tablename__ = "favorite_symbols"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relații
    user = relationship("User", back_populates="favorite_symbols")
    symbol = relationship("Symbol", back_populates="favorites")


