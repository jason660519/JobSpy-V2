# Database Schemas

## Overview

Complete database schema definitions for the JobSpy ecosystem, including PostgreSQL primary database, Redis cache structures, and ClickHouse analytics database.

## PostgreSQL Schema (Primary Database)

### Core Tables

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table - Core user management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- bcrypt hash
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    country_code VARCHAR(2), -- ISO 3166-1 alpha-2
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(5) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_metadata_gin ON users USING GIN (metadata);

-- Licenses table - License management and validation
CREATE TABLE licenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    license_key VARCHAR(255) UNIQUE NOT NULL,
    license_type VARCHAR(20) NOT NULL CHECK (license_type IN ('free', 'pro', 'enterprise')),
    hardware_fingerprint VARCHAR(255),
    device_name VARCHAR(100),
    device_os VARCHAR(50),
    app_version VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'revoked', 'expired')),
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    last_validated_at TIMESTAMP WITH TIME ZONE,
    validation_count INTEGER DEFAULT 0,
    max_validations_per_day INTEGER DEFAULT 1000,
    features JSONB DEFAULT '[]'::jsonb, -- Array of enabled features
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for licenses
CREATE INDEX idx_licenses_user_id ON licenses(user_id);
CREATE INDEX idx_licenses_license_key ON licenses(license_key);
CREATE INDEX idx_licenses_hardware_fingerprint ON licenses(hardware_fingerprint);
CREATE INDEX idx_licenses_status ON licenses(status);
CREATE INDEX idx_licenses_expires_at ON licenses(expires_at);
CREATE INDEX idx_licenses_features_gin ON licenses USING GIN (features);

-- Subscriptions table - Recurring subscription management
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    plan_type VARCHAR(50) NOT NULL CHECK (plan_type IN ('basic', 'professional', 'enterprise')),
    plan_interval VARCHAR(20) CHECK (plan_interval IN ('month', 'year')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'past_due', 'canceled', 'unpaid', 'trialing')),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    billing_cycle_anchor TIMESTAMP WITH TIME ZONE,
    price_amount INTEGER, -- in cents
    price_currency VARCHAR(3) DEFAULT 'USD',
    discount_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for subscriptions
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_subscription_id ON subscriptions(stripe_subscription_id);
CREATE INDEX idx_subscriptions_stripe_customer_id ON subscriptions(stripe_customer_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_current_period_end ON subscriptions(current_period_end);

-- Payments table - Payment transaction history
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id),
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_charge_id VARCHAR(255),
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'succeeded', 'failed', 'canceled', 'refunded')),
    payment_method_type VARCHAR(50), -- 'card', 'bank_account', etc.
    payment_method_last4 VARCHAR(4),
    payment_method_brand VARCHAR(20),
    failure_code VARCHAR(50),
    failure_message TEXT,
    description TEXT,
    receipt_email VARCHAR(255),
    receipt_url TEXT,
    refunded_amount_cents INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for payments
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_subscription_id ON payments(subscription_id);
CREATE INDEX idx_payments_stripe_payment_intent_id ON payments(stripe_payment_intent_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- API usage tracking table (partitioned by date)
CREATE TABLE api_usage (
    id UUID DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    license_id UUID REFERENCES licenses(id),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    user_agent TEXT,
    ip_address INET,
    country_code VARCHAR(2),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
) PARTITION BY RANGE (created_at);

-- Create monthly partitions for API usage
CREATE TABLE api_usage_2024_01 PARTITION OF api_usage
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE api_usage_2024_02 PARTITION OF api_usage
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Add more partitions as needed...

-- Create indexes for API usage partitions
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id, created_at);
CREATE INDEX idx_api_usage_endpoint ON api_usage(endpoint, created_at);
CREATE INDEX idx_api_usage_status_code ON api_usage(status_code, created_at);

-- User sessions table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    device_fingerprint VARCHAR(255),
    user_agent TEXT,
    ip_address INET,
    country_code VARCHAR(2),
    city VARCHAR(100),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE,
    revocation_reason VARCHAR(100)
);

-- Create indexes for sessions
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_session_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_refresh_token ON user_sessions(refresh_token);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);

-- Email verification tokens
CREATE TABLE email_verification_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Password reset tokens
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feature flags table
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT FALSE,
    rollout_percentage INTEGER DEFAULT 0 CHECK (rollout_percentage >= 0 AND rollout_percentage <= 100),
    user_criteria JSONB DEFAULT '{}'::jsonb,
    license_types VARCHAR(50)[] DEFAULT '{}'::VARCHAR[], -- Array of license types
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- System configuration table
CREATE TABLE system_config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by UUID REFERENCES users(id)
);

-- Rate limiting rules
CREATE TABLE rate_limit_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    endpoint_pattern VARCHAR(255) NOT NULL,
    license_type VARCHAR(20) NOT NULL,
    requests_per_hour INTEGER NOT NULL,
    requests_per_day INTEGER NOT NULL,
    burst_limit INTEGER NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log for important operations
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create monthly partitions for audit logs
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### Triggers and Functions

```sql
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_licenses_updated_at BEFORE UPDATE ON licenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate license keys
CREATE OR REPLACE FUNCTION generate_license_key()
RETURNS TEXT AS $$
DECLARE
    chars TEXT := 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    result TEXT := '';
    i INTEGER;
BEGIN
    -- Generate format: XXXX-XXXX-XXXX-XXXX
    FOR i IN 1..16 LOOP
        IF i IN (5, 9, 13) THEN
            result := result || '-';
        END IF;
        result := result || substr(chars, floor(random() * length(chars) + 1)::integer, 1);
    END LOOP;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to check license validation rate limits
CREATE OR REPLACE FUNCTION check_license_rate_limit(
    p_license_id UUID,
    p_max_validations INTEGER DEFAULT 1000
)
RETURNS BOOLEAN AS $$
DECLARE
    validation_count INTEGER;
BEGIN
    -- Count validations in the last 24 hours
    SELECT COUNT(*)
    INTO validation_count
    FROM api_usage
    WHERE license_id = p_license_id
    AND endpoint = '/licenses/validate'
    AND created_at > NOW() - INTERVAL '24 hours';
    
    RETURN validation_count < p_max_validations;
END;
$$ LANGUAGE plpgsql;
```

### Views for Common Queries

```sql
-- Active licenses view
CREATE VIEW active_licenses AS
SELECT 
    l.*,
    u.email,
    u.first_name,
    u.last_name,
    s.plan_type as subscription_plan,
    s.status as subscription_status
FROM licenses l
JOIN users u ON l.user_id = u.id
LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active'
WHERE l.status = 'active'
AND (l.expires_at IS NULL OR l.expires_at > NOW());

-- User analytics view
CREATE VIEW user_analytics AS
SELECT 
    u.id,
    u.email,
    u.created_at as user_created_at,
    l.license_type,
    l.created_at as license_created_at,
    s.plan_type as subscription_plan,
    s.status as subscription_status,
    COUNT(au.id) as api_calls_last_30_days,
    MAX(au.created_at) as last_api_call
FROM users u
LEFT JOIN licenses l ON u.id = l.user_id AND l.status = 'active'
LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active'
LEFT JOIN api_usage au ON u.id = au.user_id AND au.created_at > NOW() - INTERVAL '30 days'
WHERE u.status = 'active'
GROUP BY u.id, u.email, u.created_at, l.license_type, l.created_at, s.plan_type, s.status;

-- Revenue analytics view
CREATE VIEW revenue_analytics AS
SELECT 
    DATE_TRUNC('month', p.created_at) as month,
    COUNT(DISTINCT p.user_id) as paying_customers,
    COUNT(p.id) as total_payments,
    SUM(p.amount_cents) as total_revenue_cents,
    AVG(p.amount_cents) as avg_payment_cents,
    s.plan_type
FROM payments p
JOIN subscriptions s ON p.subscription_id = s.id
WHERE p.status = 'succeeded'
GROUP BY DATE_TRUNC('month', p.created_at), s.plan_type
ORDER BY month DESC;
```

## Redis Schema (Cache & Sessions)

### Data Structures

```javascript
// Session management
// Key pattern: session:{session_token}
// TTL: 24 hours (86400 seconds)
{
  "user_id": "uuid",
  "email": "user@example.com",
  "license_type": "pro",
  "permissions": ["api_access", "premium_features", "export_data"],
  "device_fingerprint": "hardware_hash",
  "last_activity": "2024-01-01T12:00:00Z",
  "ip_address": "192.168.1.1",
  "country_code": "US"
}

// License validation cache
// Key pattern: license:{license_key}
// TTL: 1 hour (3600 seconds)
{
  "valid": true,
  "user_id": "uuid",
  "license_type": "pro",
  "hardware_fingerprint": "hardware_hash",
  "features": ["unlimited_search", "export_data", "premium_api"],
  "expires_at": "2025-01-01T00:00:00Z",
  "last_validated": "2024-01-01T12:00:00Z"
}

// Rate limiting
// Key pattern: rate_limit:{user_id}:{endpoint}
// TTL: 1 hour (3600 seconds)
{
  "count": 150,
  "window_start": "2024-01-01T12:00:00Z",
  "limit": 1000,
  "reset_time": "2024-01-01T13:00:00Z"
}

// API response cache
// Key pattern: cache:salary:{job_title}:{location}:{experience}
// TTL: 24 hours (86400 seconds)
{
  "data": {
    "salary_range": {"min": 80000, "max": 150000, "median": 115000},
    "market_percentiles": {"25th": 90000, "50th": 115000, "75th": 140000},
    "experience_breakdown": [...],
    "trending_direction": "up"
  },
  "cached_at": "2024-01-01T12:00:00Z",
  "source": "aggregated",
  "sample_size": 1250
}

// User preferences cache
// Key pattern: user_prefs:{user_id}
// TTL: 7 days (604800 seconds)
{
  "theme": "dark",
  "language": "en",
  "timezone": "America/New_York",
  "notification_preferences": {
    "email_alerts": true,
    "push_notifications": false,
    "weekly_reports": true
  },
  "search_defaults": {
    "job_sites": ["indeed", "linkedin"],
    "results_per_page": 50,
    "sort_by": "date"
  }
}

// Feature flags cache
// Key pattern: feature_flags
// TTL: 5 minutes (300 seconds)
{
  "advanced_search": {"enabled": true, "rollout": 100},
  "new_ui_beta": {"enabled": true, "rollout": 25},
  "api_v2": {"enabled": false, "rollout": 0}
}

// System metrics cache
// Key pattern: metrics:{metric_name}:{timestamp}
// TTL: 1 hour (3600 seconds)
{
  "active_users_24h": 1250,
  "api_calls_last_hour": 15000,
  "error_rate_percentage": 0.02,
  "avg_response_time_ms": 145
}
```

### Redis Configuration

```redis
# Redis configuration for JobSpy
# /etc/redis/redis.conf

# Basic settings
bind 0.0.0.0
port 6379
timeout 300
tcp-keepalive 300

# Memory settings
maxmemory 4gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Persistence settings
save 900 1
save 300 10
save 60 10000

# Append only file
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# Security
requirepass your_redis_password_here

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Performance tuning
tcp-backlog 511
databases 16
```

## ClickHouse Schema (Analytics Database)

### Event Tracking Tables

```sql
-- User events for behavioral analytics
CREATE TABLE user_events (
    event_id UUID,
    user_id UUID,
    session_id UUID,
    event_type LowCardinality(String), -- 'page_view', 'search', 'export', 'upgrade'
    event_category LowCardinality(String), -- 'engagement', 'conversion', 'retention'
    event_data String, -- JSON string with event details
    page_url String,
    referrer String,
    user_agent String,
    ip_address IPv4,
    country_code LowCardinality(String),
    city String,
    device_type LowCardinality(String), -- 'desktop', 'mobile', 'tablet'
    browser LowCardinality(String),
    os LowCardinality(String),
    timestamp DateTime64(3) DEFAULT now64(),
    date Date DEFAULT today() MATERIALIZED
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (user_id, timestamp)
TTL date + INTERVAL 2 YEAR;

-- Business events for revenue analytics
CREATE TABLE business_events (
    event_id UUID,
    user_id UUID,
    event_type LowCardinality(String), -- 'subscription', 'payment', 'refund', 'churn'
    amount_cents UInt32,
    currency LowCardinality(String),
    plan_type LowCardinality(String), -- 'free', 'pro', 'enterprise'
    payment_method LowCardinality(String),
    stripe_event_id String,
    subscription_id String,
    trial_period Boolean,
    discount_amount UInt32,
    discount_code String,
    timestamp DateTime64(3) DEFAULT now64(),
    date Date DEFAULT today() MATERIALIZED,
    metadata String -- JSON string
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (timestamp, user_id)
TTL date + INTERVAL 5 YEAR;

-- API usage metrics for performance monitoring
CREATE TABLE api_metrics (
    request_id UUID,
    user_id UUID,
    license_id UUID,
    endpoint LowCardinality(String),
    method LowCardinality(String), -- 'GET', 'POST', 'PUT', 'DELETE'
    status_code UInt16,
    response_time_ms UInt32,
    request_size_bytes UInt32,
    response_size_bytes UInt32,
    cache_hit Boolean DEFAULT false,
    error_message String,
    server_id LowCardinality(String),
    server_region LowCardinality(String),
    timestamp DateTime64(3) DEFAULT now64(),
    date Date DEFAULT today() MATERIALIZED
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (timestamp, endpoint)
TTL date + INTERVAL 1 YEAR;

-- License validation events
CREATE TABLE license_validations (
    validation_id UUID,
    user_id UUID,
    license_id UUID,
    license_key String,
    hardware_fingerprint String,
    app_version String,
    validation_result LowCardinality(String), -- 'success', 'invalid_key', 'expired', 'hardware_mismatch'
    ip_address IPv4,
    country_code LowCardinality(String),
    timestamp DateTime64(3) DEFAULT now64(),
    date Date DEFAULT today() MATERIALIZED
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (user_id, timestamp)
TTL date + INTERVAL 1 YEAR;

-- Job search analytics
CREATE TABLE job_searches (
    search_id UUID,
    user_id UUID,
    license_type LowCardinality(String),
    job_title String,
    location String,
    job_sites Array(LowCardinality(String)),
    results_found UInt32,
    search_duration_ms UInt32,
    filters_applied String, -- JSON string
    export_format LowCardinality(String), -- '', 'csv', 'json', 'xlsx'
    timestamp DateTime64(3) DEFAULT now64(),
    date Date DEFAULT today() MATERIALIZED
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (user_id, timestamp)
TTL date + INTERVAL 1 YEAR;
```

### Materialized Views for Analytics

```sql
-- Daily user activity summary
CREATE MATERIALIZED VIEW daily_user_activity
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, user_id)
AS SELECT
    date,
    user_id,
    countState() AS events_count,
    uniqState(session_id) AS sessions_count,
    minState(timestamp) AS first_event_time,
    maxState(timestamp) AS last_event_time
FROM user_events
GROUP BY date, user_id;

-- Hourly API performance metrics
CREATE MATERIALIZED VIEW hourly_api_performance
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, hour, endpoint)
AS SELECT
    date,
    toHour(timestamp) AS hour,
    endpoint,
    countState() AS request_count,
    avgState(response_time_ms) AS avg_response_time,
    quantileState(0.95)(response_time_ms) AS p95_response_time,
    sumState(request_size_bytes) AS total_request_bytes,
    sumState(response_size_bytes) AS total_response_bytes,
    countIfState(status_code >= 400) AS error_count
FROM api_metrics
GROUP BY date, hour, endpoint;

-- Monthly revenue summary
CREATE MATERIALIZED VIEW monthly_revenue
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, plan_type)
AS SELECT
    toStartOfMonth(date) AS date,
    plan_type,
    countState() AS transaction_count,
    sumState(amount_cents) AS total_revenue_cents,
    uniqState(user_id) AS unique_customers
FROM business_events
WHERE event_type = 'payment'
GROUP BY toStartOfMonth(date), plan_type;

-- User cohort analysis
CREATE MATERIALIZED VIEW user_cohorts
ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(registration_month)
ORDER BY (registration_month, user_id)
AS SELECT
    user_id,
    toStartOfMonth(min(date)) AS registration_month,
    min(date) AS registration_date,
    max(date) AS last_activity_date,
    count() AS total_events,
    uniq(date) AS active_days
FROM user_events
GROUP BY user_id;
```

### Sample Queries for Analytics

```sql
-- Daily Active Users (DAU)
SELECT 
    date,
    uniq(user_id) AS dau
FROM user_events
WHERE date >= today() - 30
GROUP BY date
ORDER BY date;

-- Conversion funnel analysis
SELECT 
    event_type,
    count() AS users,
    count() / (SELECT count() FROM user_events WHERE event_type = 'registration') AS conversion_rate
FROM user_events
WHERE event_type IN ('registration', 'first_search', 'export_data', 'upgrade_to_pro')
GROUP BY event_type
ORDER BY users DESC;

-- Revenue by plan type over time
SELECT 
    toStartOfMonth(date) AS month,
    plan_type,
    sum(amount_cents) / 100 AS revenue_usd,
    count() AS transactions,
    uniq(user_id) AS customers
FROM business_events
WHERE event_type = 'payment' AND date >= today() - 365
GROUP BY month, plan_type
ORDER BY month, plan_type;

-- API performance trends
SELECT 
    toStartOfHour(timestamp) AS hour,
    endpoint,
    count() AS requests,
    avg(response_time_ms) AS avg_response_time,
    quantile(0.95)(response_time_ms) AS p95_response_time,
    countIf(status_code >= 400) AS errors,
    errors / requests AS error_rate
FROM api_metrics
WHERE timestamp >= now() - INTERVAL 24 HOUR
GROUP BY hour, endpoint
ORDER BY hour, endpoint;

-- User retention analysis
SELECT 
    registration_month,
    count() AS cohort_size,
    countIf(last_activity_date >= registration_date + INTERVAL 30 DAY) AS retained_30d,
    retained_30d / cohort_size AS retention_rate_30d
FROM user_cohorts
WHERE registration_month >= toStartOfMonth(today() - INTERVAL 12 MONTH)
GROUP BY registration_month
ORDER BY registration_month;
```

---

**Note**: This database schema is designed for scalability, performance, and comprehensive analytics. The schema includes proper indexing, partitioning strategies, and materialized views for common analytics queries.