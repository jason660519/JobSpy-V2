"""
System configuration and monitoring models
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SystemConfig(Base):
    """System configuration settings"""
    
    __tablename__ = "system_config"
    
    key: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Configuration metadata
    category: Mapped[str] = mapped_column(String(100))
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1)
    previous_value: Mapped[Optional[str]] = mapped_column(Text)
    
    def __repr__(self) -> str:
        return f"<SystemConfig(key={self.key})>"


class ApiUsageLog(Base):
    """API usage tracking and monitoring"""
    
    __tablename__ = "api_usage_logs"
    
    # Request details
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String, index=True)
    
    # Request/Response details
    request_size: Mapped[Optional[int]] = mapped_column(Integer)
    response_size: Mapped[Optional[int]] = mapped_column(Integer)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Performance metrics
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    database_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    ai_processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Client information
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_type: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Indexes for monitoring
    __table_args__ = (
        Index('idx_api_endpoint_time', 'endpoint', 'created_at'),
        Index('idx_api_user_time', 'user_id', 'created_at'),
        Index('idx_api_status_time', 'status_code', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<ApiUsageLog(endpoint={self.endpoint}, status={self.status_code})>"


class SystemHealth(Base):
    """System health monitoring metrics"""
    
    __tablename__ = "system_health"
    
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_unit: Mapped[str] = mapped_column(String(50))
    
    # Health status
    status: Mapped[str] = mapped_column(String(20))  # healthy, warning, critical
    threshold_min: Mapped[Optional[float]] = mapped_column(Float)
    threshold_max: Mapped[Optional[float]] = mapped_column(Float)
    
    # Additional metadata
    component: Mapped[str] = mapped_column(String(100))  # database, api, ai, cache
    environment: Mapped[str] = mapped_column(String(50))  # dev, staging, prod
    
    def __repr__(self) -> str:
        return f"<SystemHealth(metric={self.metric_name}, value={self.metric_value})>"


class DataSource(Base):
    """Configuration and monitoring for external data sources"""
    
    __tablename__ = "data_sources"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    source_type: Mapped[str] = mapped_column(String(50))  # api, scraping, rss
    base_url: Mapped[str] = mapped_column(String(500))
    
    # Authentication and configuration
    auth_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    request_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    rate_limits: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Status and health
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_success: Mapped[Optional[datetime]] = mapped_column()
    last_error: Mapped[Optional[datetime]] = mapped_column()
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[Optional[float]] = mapped_column(Float)
    
    # Performance metrics
    avg_response_time: Mapped[Optional[float]] = mapped_column(Float)
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, default=0)
    
    def __repr__(self) -> str:
        return f"<DataSource(name={self.name}, type={self.source_type})>"