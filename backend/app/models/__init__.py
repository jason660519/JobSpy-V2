"""
Database models package

This package contains all SQLAlchemy database models for the JobSpy v2 application.
"""

from .base import Base
from .user import User
from .job import JobListing, JobBookmark
from .search import SearchLog, UserAnalytics
from .ai import AIAnalysisCache, AIUsageStats, JobAnalysisResult
from .system import SystemConfig, ApiUsageLog, SystemHealth, DataSource

__all__ = [
    # Base model
    "Base",
    
    # User models
    "User",
    
    # Job models
    "JobListing",
    "JobBookmark",
    
    # Search and analytics models
    "SearchLog",
    "UserAnalytics",
    
    # AI models
    "AIAnalysisCache",
    "AIUsageStats",
    "JobAnalysisResult",
    
    # System models
    "SystemConfig",
    "ApiUsageLog",
    "SystemHealth",
    "DataSource",
]