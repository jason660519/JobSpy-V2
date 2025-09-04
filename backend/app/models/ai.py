"""
AI analysis and caching models
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AIAnalysisCache(Base):
    """Cache for AI analysis results to reduce costs and improve performance"""
    
    __tablename__ = "ai_analysis_cache"
    
    # URL and content identification
    url_hash: Mapped[str] = mapped_column(
        String(64), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    original_url: Mapped[str] = mapped_column(String(1000))
    content_hash: Mapped[Optional[str]] = mapped_column(String(64))
    
    # Analysis results
    analysis_result: Mapped[dict] = mapped_column(JSONB, nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(50))  # vision, text, hybrid
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Cost and performance tracking
    cost_used: Mapped[Optional[float]] = mapped_column(Float)
    model_used: Mapped[str] = mapped_column(String(100))
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Cache management
    expires_at: Mapped[Optional[datetime]] = mapped_column(index=True)
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[Optional[datetime]] = mapped_column()
    
    # Quality metrics
    accuracy_rating: Mapped[Optional[float]] = mapped_column(Float)
    human_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_ai_cache_url_expires', 'url_hash', 'expires_at'),
        Index('idx_ai_cache_model_created', 'model_used', 'created_at'),
        Index('idx_ai_cache_cost_date', 'cost_used', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<AIAnalysisCache(id={self.id}, model={self.model_used})>"


class AIUsageStats(Base):
    """Track AI usage statistics for cost management and optimization"""
    
    __tablename__ = "ai_usage_stats"
    
    # Date and user tracking
    date: Mapped[datetime] = mapped_column(nullable=False, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    
    # Usage metrics
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, default=0)
    failed_requests: Mapped[int] = mapped_column(Integer, default=0)
    
    # Cost tracking
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    
    # Model usage breakdown
    model_usage: Mapped[dict] = mapped_column(JSONB)  # {model_name: usage_count}
    
    # Performance metrics
    avg_processing_time: Mapped[Optional[float]] = mapped_column(Float)
    cache_hit_rate: Mapped[Optional[float]] = mapped_column(Float)
    
    def __repr__(self) -> str:
        return f"<AIUsageStats(date={self.date}, total_cost={self.total_cost})>"


class JobAnalysisResult(Base):
    """Store detailed AI analysis results for job listings"""
    
    __tablename__ = "job_analysis_results"
    
    job_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )
    
    # Analysis details
    analysis_type: Mapped[str] = mapped_column(String(50))
    analysis_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Extracted structured data
    extracted_skills: Mapped[Optional[list]] = mapped_column(JSONB)
    extracted_requirements: Mapped[Optional[list]] = mapped_column(JSONB)
    salary_analysis: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Quality scores
    relevance_score: Mapped[Optional[float]] = mapped_column(Float)
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    completeness_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Analysis metadata
    model_version: Mapped[str] = mapped_column(String(50))
    analysis_cost: Mapped[Optional[float]] = mapped_column(Float)
    
    def __repr__(self) -> str:
        return f"<JobAnalysisResult(job_id={self.job_id}, type={self.analysis_type})>"