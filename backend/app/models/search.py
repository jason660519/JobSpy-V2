"""
Search logging and user analytics models
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text, Float, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class SearchLog(Base):
    """Search log model for tracking user search behavior"""
    
    __tablename__ = "search_logs"
    
    # User association (optional for anonymous searches)
    user_id: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey("users.id"),
        index=True
    )
    
    # Search query details
    query_text: Mapped[str] = mapped_column(
        Text, 
        nullable=False,
        index=True
    )
    
    # Search filters and parameters
    filters: Mapped[Optional[dict]] = mapped_column(JSONB)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    job_type: Mapped[Optional[str]] = mapped_column(String(50))
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))
    salary_range: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Search results and performance
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    sources_used: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # AI enhancement tracking
    ai_used: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_cost: Mapped[Optional[float]] = mapped_column(Float)
    ai_processing_time: Mapped[Optional[int]] = mapped_column(Integer)
    
    # User interaction tracking
    clicked_results: Mapped[Optional[list]] = mapped_column(JSONB)
    bookmarked_jobs: Mapped[Optional[list]] = mapped_column(JSONB)
    session_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Search quality metrics
    user_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5 rating
    search_success: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    # Relationships
    user = relationship("User", back_populates="search_logs")
    
    # Indexes for analytics
    __table_args__ = (
        Index('idx_search_user_created', 'user_id', 'created_at'),
        Index('idx_search_query_created', 'query_text', 'created_at'),
        Index('idx_search_filters', 'location', 'job_type', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<SearchLog(id={self.id}, query={self.query_text[:50]})>"


class UserAnalytics(Base):
    """User analytics and behavior tracking"""
    
    __tablename__ = "user_analytics"
    
    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # User profile analytics
    search_preferences: Mapped[Optional[dict]] = mapped_column(JSONB)
    skill_interests: Mapped[Optional[list]] = mapped_column(JSONB)
    location_preferences: Mapped[Optional[list]] = mapped_column(JSONB)
    salary_expectations: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Usage statistics
    total_searches: Mapped[int] = mapped_column(Integer, default=0)
    total_bookmarks: Mapped[int] = mapped_column(Integer, default=0)
    avg_session_duration: Mapped[Optional[float]] = mapped_column(Float)
    last_active: Mapped[Optional[datetime]] = mapped_column()
    
    # Recommendation metrics
    recommendation_score: Mapped[Optional[float]] = mapped_column(Float)
    engagement_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Relationships
    user = relationship("User", back_populates="user_analytics")
    
    def __repr__(self) -> str:
        return f"<UserAnalytics(user_id={self.user_id})>"