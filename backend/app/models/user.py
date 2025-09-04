"""
User model for authentication and user management
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    """User model for storing user account information"""
    
    __tablename__ = "users"
    
    # Basic user information
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # User profile information
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False
    )
    
    is_verified: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False
    )
    
    # User preferences and profile data stored as JSON
    profile: Mapped[Optional[dict]] = mapped_column(JSONB)
    preferences: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Timestamps for security tracking
    last_login: Mapped[Optional[datetime]] = mapped_column()
    password_changed_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    search_logs = relationship("SearchLog", back_populates="user", cascade="all, delete-orphan")
    job_bookmarks = relationship("JobBookmark", back_populates="user", cascade="all, delete-orphan")
    user_analytics = relationship("UserAnalytics", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"