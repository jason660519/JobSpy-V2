"""
Job listing model for storing scraped job information
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, Integer, String, Text, Index, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class JobListing(Base):
    """Job listing model for storing job information from various sources"""
    
    __tablename__ = "job_listings"
    
    # Basic job information
    title: Mapped[str] = mapped_column(
        String(500), 
        nullable=False,
        index=True
    )
    
    company: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        index=True
    )
    
    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        index=True
    )
    
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Job requirements and skills
    requirements: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    skills_required: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Salary and compensation
    salary_range: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Job characteristics
    job_type: Mapped[Optional[str]] = mapped_column(String(50))  # full-time, part-time, contract
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))  # entry, mid, senior
    remote_friendly: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Source information
    source: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        index=True
    )
    
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    source_job_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Raw data from scraping
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # AI analysis results
    ai_analysis: Mapped[Optional[dict]] = mapped_column(JSONB)
    ai_score: Mapped[Optional[float]] = mapped_column()
    
    # Timestamps
    posted_date: Mapped[Optional[datetime]] = mapped_column(index=True)
    scraped_date: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # Status tracking
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    bookmarks = relationship("JobBookmark", back_populates="job", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_job_title_company', 'title', 'company'),
        Index('idx_job_location_type', 'location', 'job_type'),
        Index('idx_job_posted_scraped', 'posted_date', 'scraped_date'),
        Index('idx_job_source_active', 'source', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f"<JobListing(id={self.id}, title={self.title}, company={self.company})>"


class JobBookmark(Base):
    """User bookmarks for job listings"""
    
    __tablename__ = "job_bookmarks"
    
    user_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    job_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("job_listings.id"),
        nullable=False,
        index=True
    )
    
    notes: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    
    # Application status tracking
    application_status: Mapped[Optional[str]] = mapped_column(String(50))
    applied_date: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    user = relationship("User", back_populates="job_bookmarks")
    job = relationship("JobListing", back_populates="bookmarks")
    
    __table_args__ = (
        Index('idx_bookmark_user_job', 'user_id', 'job_id', unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<JobBookmark(user_id={self.user_id}, job_id={self.job_id})>"