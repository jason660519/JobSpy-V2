# Technical Architecture

## Overview

This section provides comprehensive technical architecture documentation for the JobSpy ecosystem, including system design, data flow, database schemas, API specifications, and security architecture.

## System Architecture Overview

### High-Level Architecture Diagram

```
                    ┌─────────────────────────────────────────┐
                    │              JobSpy Ecosystem           │
                    └─────────────────────────────────────────┘
                                         │
           ┌─────────────────────────────┼─────────────────────────────┐
           │                             │                             │
    ┌─────────────┐              ┌─────────────┐              ┌─────────────┐
    │   Client    │              │   Backend   │              │   External  │
    │Applications │              │  Services   │              │  Services   │
    └─────────────┘              └─────────────┘              └─────────────┘
           │                             │                             │
    ┌──────┼──────┐               ┌──────┼──────┐               ┌──────┼──────┐
    │      │      │               │      │      │               │      │      │
 Desktop Browser PWA         License Premium Admin          Stripe Job   Payment
   App   Extension App        Server   API   Dashboard       API   Sites  Gateway
```

### Component Architecture

#### 1. Client-Side Applications

**Desktop Application (Primary)**
```
┌─────────────────────────────────────────┐
│            Electron Main Process        │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────────┐│
│  │    React    │  │   Python Backend    ││
│  │   Frontend  │  │   (JobSpy Core)     ││
│  │             │  │                     ││
│  │ - Job Search│  │ - Site Scraping     ││
│  │ - Results   │  │ - Data Processing   ││
│  │ - Settings  │  │ - Local Storage     ││
│  │ - License   │  │ - Export Functions  ││
│  └─────────────┘  └─────────────────────┘│
│         │                    │           │
│  ┌─────────────────────────────────────┐ │
│  │        IPC Communication            │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
         │                    │
         ▼                    ▼
   License Server    Job Sites (Direct)
```

**Browser Extension (Secondary)**
```
┌─────────────────────────────────────────┐
│           Browser Extension             │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────────┐│
│  │   Popup     │  │   Content Scripts   ││
│  │     UI      │  │                     ││
│  │             │  │ - Site Integration  ││
│  │ - Controls  │  │ - Data Extraction   ││
│  │ - Results   │  │ - DOM Manipulation  ││
│  │ - Settings  │  │ - Event Handling    ││
│  └─────────────┘  └─────────────────────┘│
│         │                    │           │
│  ┌─────────────────────────────────────┐ │
│  │      Background Service Worker      │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
         │                    │
         ▼                    ▼
   Premium API        Job Sites (Injected)
```

#### 2. Backend Services Architecture

**Service Layer Design**
```
┌─────────────────────────────────────────────────────────┐
│                   API Gateway / Load Balancer           │
│                      (Cloudflare)                       │
└─────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────────────┐    ┌─────────────────┐    ┌──────────────┐
│ License Server│    │  Premium Data   │    │ Payment &    │
│   (Node.js)   │    │ API (FastAPI)   │    │Subscription  │
│               │    │                 │    │ Management   │
│ - Auth/Valid  │    │ - Salary Data   │    │ (Stripe)     │
│ - Hardware FP │    │ - Company Info  │    │              │
│ - Rate Limit  │    │ - Market Trends │    │ - Billing    │
│ - User Mgmt   │    │ - Career Intel  │    │ - Webhooks   │
└───────────────┘    └─────────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                   Data Layer                            │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │ PostgreSQL  │ │    Redis    │ │     ClickHouse      │ │
│ │             │ │             │ │                     │ │
│ │ - Users     │ │ - Sessions  │ │ - Analytics Data    │ │
│ │ - Licenses  │ │ - Cache     │ │ - Usage Metrics     │ │
│ │ - Payments  │ │ - Rate Lmts │ │ - Business Reports  │ │
│ │ - Settings  │ │ - Temp Data │ │ - Performance Logs  │ │
│ └─────────────┘ └─────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Data Architecture

### Database Schema Design

#### PostgreSQL (Primary Database)

```sql
-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB
);

-- License Management
CREATE TABLE licenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    license_key VARCHAR(255) UNIQUE NOT NULL,
    license_type VARCHAR(50) NOT NULL, -- 'free', 'pro', 'enterprise'
    hardware_fingerprint VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    last_validated_at TIMESTAMP,
    validation_count INTEGER DEFAULT 0,
    metadata JSONB
);

-- Subscription Management
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    stripe_subscription_id VARCHAR(255) UNIQUE,
    plan_type VARCHAR(50) NOT NULL, -- 'basic', 'pro', 'enterprise'
    status VARCHAR(50) NOT NULL, -- 'active', 'canceled', 'past_due'
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- API Usage Tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
) PARTITION BY RANGE (created_at);

-- Payment History
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Performance optimized indexes
CREATE INDEX idx_licenses_user_id ON licenses(user_id);
CREATE INDEX idx_licenses_hardware_fp ON licenses(hardware_fingerprint);
CREATE INDEX idx_licenses_key ON licenses(license_key);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id);
CREATE INDEX idx_api_usage_user_date ON api_usage(user_id, created_at);
CREATE INDEX idx_payments_user_id ON payments(user_id);
```

#### Redis (Caching & Sessions)

```javascript
// Redis data structure design

// User sessions
// Key: session:{session_id}
// TTL: 24 hours
{
  "user_id": "uuid",
  "email": "user@example.com",
  "license_type": "pro",
  "permissions": ["api_access", "premium_features"],
  "last_activity": "2024-01-01T12:00:00Z"
}

// Rate limiting
// Key: rate_limit:{user_id}:{endpoint}
// TTL: 1 hour
{
  "count": 150,
  "window_start": "2024-01-01T12:00:00Z",
  "limit": 1000
}

// API response cache
// Key: cache:salary_data:{job_title}:{location}
// TTL: 24 hours
{
  "data": {...},
  "cached_at": "2024-01-01T12:00:00Z",
  "expires_at": "2024-01-02T12:00:00Z"
}

// License validation cache
// Key: license:{license_key}
// TTL: 1 hour
{
  "valid": true,
  "user_id": "uuid",
  "license_type": "pro",
  "hardware_fingerprint": "hash",
  "last_validated": "2024-01-01T12:00:00Z"
}
```

#### ClickHouse (Analytics)

```sql
-- Business Analytics Schema
CREATE TABLE user_events (
    event_id UUID,
    user_id UUID,
    event_type LowCardinality(String),
    event_data String,
    timestamp DateTime64(3),
    session_id UUID,
    user_agent String,
    ip_address IPv4,
    country_code LowCardinality(String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp);

-- Revenue Analytics
CREATE TABLE revenue_events (
    event_id UUID,
    user_id UUID,
    event_type LowCardinality(String), -- 'purchase', 'subscription', 'refund'
    amount_cents UInt32,
    currency LowCardinality(String),
    plan_type LowCardinality(String),
    timestamp DateTime64(3),
    stripe_event_id String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, user_id);

-- API Performance Metrics
CREATE TABLE api_metrics (
    request_id UUID,
    user_id UUID,
    endpoint LowCardinality(String),
    method LowCardinality(String),
    status_code UInt16,
    response_time_ms UInt32,
    request_size_bytes UInt32,
    response_size_bytes UInt32,
    timestamp DateTime64(3),
    server_id LowCardinality(String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, endpoint);
```

## API Architecture

### License Server API

**Base URL**: `https://license.jobspy.com/api/v1`

```yaml
# OpenAPI 3.0 Specification
openapi: 3.0.0
info:
  title: JobSpy License Server API
  version: 1.0.0
  description: License validation and user management

paths:
  /auth/register:
    post:
      summary: Register new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 8
                hardware_fingerprint:
                  type: string
      responses:
        201:
          description: User created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  user_id:
                    type: string
                    format: uuid
                  license_key:
                    type: string
                  license_type:
                    type: string
                    enum: [free, pro, enterprise]

  /licenses/validate:
    post:
      summary: Validate license key
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                license_key:
                  type: string
                hardware_fingerprint:
                  type: string
                app_version:
                  type: string
      responses:
        200:
          description: License validation result
          content:
            application/json:
              schema:
                type: object
                properties:
                  valid:
                    type: boolean
                  license_type:
                    type: string
                  expires_at:
                    type: string
                    format: date-time
                  features:
                    type: array
                    items:
                      type: string

  /users/{user_id}/subscription:
    get:
      summary: Get user subscription status
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: Subscription information
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: [active, canceled, past_due]
                  plan_type:
                    type: string
                  current_period_end:
                    type: string
                    format: date-time
```

### Premium Data API

**Base URL**: `https://api.jobspy.com/api/v1`

```yaml
# Premium Data API Specification
paths:
  /premium/salary-insights:
    post:
      summary: Get salary insights for job position
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                job_title:
                  type: string
                location:
                  type: string
                experience_years:
                  type: integer
                company_size:
                  type: string
                  enum: [startup, small, medium, large, enterprise]
      responses:
        200:
          description: Salary insights data
          content:
            application/json:
              schema:
                type: object
                properties:
                  job_title:
                    type: string
                  location:
                    type: string
                  salary_range:
                    type: object
                    properties:
                      min:
                        type: integer
                      max:
                        type: integer
                      median:
                        type: integer
                      average:
                        type: integer
                  market_percentiles:
                    type: object
                    properties:
                      25th:
                        type: integer
                      50th:
                        type: integer
                      75th:
                        type: integer
                      90th:
                        type: integer
                  data_freshness:
                    type: string
                  sample_size:
                    type: integer

  /premium/company-insights:
    post:
      summary: Get comprehensive company information
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                company_name:
                  type: string
      responses:
        200:
          description: Company insights data
          content:
            application/json:
              schema:
                type: object
                properties:
                  company_name:
                    type: string
                  industry:
                    type: string
                  size_range:
                    type: string
                  rating:
                    type: number
                    format: float
                  culture_scores:
                    type: object
                    properties:
                      diversity:
                        type: number
                      innovation:
                        type: number
                      work_life_balance:
                        type: number
                  hiring_trends:
                    type: object
                  recent_news:
                    type: array
                    items:
                      type: object
```

## Security Architecture

### Authentication & Authorization

```javascript
// JWT Token Structure
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "key-id-1"
  },
  "payload": {
    "sub": "user-uuid",
    "email": "user@example.com",
    "license_type": "pro",
    "permissions": [
      "api:premium_data",
      "features:unlimited_search",
      "features:export_data"
    ],
    "iat": 1640995200,
    "exp": 1640998800,
    "iss": "license.jobspy.com",
    "aud": "api.jobspy.com"
  }
}

// Hardware Fingerprint Generation
function generateHardwareFingerprint() {
  const components = [
    os.hostname(),
    os.cpus()[0].model,
    os.totalmem().toString(),
    os.arch(),
    os.platform(),
    // Additional entropy from network interfaces
    Object.keys(os.networkInterfaces()).sort().join('|')
  ];
  
  return crypto
    .createHash('sha256')
    .update(components.join('|'))
    .digest('hex');
}
```

### Encryption & Data Protection

```javascript
// Data Encryption Strategy
const encryption = {
  // At-rest encryption for sensitive data
  sensitiveFields: {
    algorithm: 'aes-256-gcm',
    keyRotation: '90-days',
    fields: ['email', 'payment_methods', 'personal_data']
  },
  
  // In-transit encryption
  transport: {
    tls: 'TLS 1.3',
    certificateAuthority: 'Let\'s Encrypt',
    hsts: 'max-age=31536000; includeSubDomains'
  },
  
  // Application-level encryption
  application: {
    secrets: 'AWS Secrets Manager',
    environment: 'Encrypted environment variables',
    database: 'PostgreSQL TDE (Transparent Data Encryption)'
  }
};

// API Rate Limiting
const rateLimiting = {
  tiers: {
    free: { requests: 100, window: '1 hour' },
    pro: { requests: 1000, window: '1 hour' },
    enterprise: { requests: 10000, window: '1 hour' }
  },
  
  implementation: 'Redis sliding window',
  headers: ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset']
};
```

## Performance Architecture

### Caching Strategy

```javascript
// Multi-layer caching implementation
const cachingLayers = {
  L1_Memory: {
    technology: 'Node.js in-memory cache',
    ttl: '5 minutes',
    use_case: 'Frequently accessed data within single instance'
  },
  
  L2_Redis: {
    technology: 'Redis cluster',
    ttl: '1 hour to 24 hours',
    use_case: 'Shared cache across multiple instances'
  },
  
  L3_CDN: {
    technology: 'Cloudflare CDN',
    ttl: '7 days',
    use_case: 'Static assets and API responses'
  },
  
  L4_Database: {
    technology: 'PostgreSQL query cache',
    ttl: 'Query-dependent',
    use_case: 'Database query result caching'
  }
};

// Cache invalidation strategy
function invalidateCache(patterns) {
  // Pattern-based cache invalidation
  const keys = await redis.keys(pattern);
  await redis.del(...keys);
  
  // Pub/sub for distributed cache invalidation
  await redis.publish('cache:invalidate', JSON.stringify({
    patterns,
    timestamp: Date.now()
  }));
}
```

### Database Performance

```sql
-- Database performance optimizations

-- Connection pooling configuration
-- max_connections = 100
-- shared_buffers = 25% of RAM
-- effective_cache_size = 75% of RAM

-- Query optimization
EXPLAIN (ANALYZE, BUFFERS) 
SELECT u.email, l.license_type, s.status 
FROM users u
JOIN licenses l ON u.id = l.user_id
LEFT JOIN subscriptions s ON u.id = s.user_id
WHERE l.status = 'active';

-- Partitioning strategy for large tables
CREATE TABLE api_usage_y2024m01 PARTITION OF api_usage
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Materialized views for complex analytics
CREATE MATERIALIZED VIEW user_analytics AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    license_type,
    COUNT(*) as user_count,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_users
FROM users u
JOIN licenses l ON u.id = l.user_id
GROUP BY DATE_TRUNC('day', created_at), license_type;
```

## Monitoring & Observability

### Metrics Collection

```javascript
// Application metrics
const metrics = {
  business: {
    daily_active_users: 'gauge',
    conversion_rate: 'gauge', 
    monthly_recurring_revenue: 'gauge',
    customer_lifetime_value: 'gauge'
  },
  
  technical: {
    api_response_time: 'histogram',
    error_rate: 'counter',
    database_connection_pool: 'gauge',
    cache_hit_ratio: 'gauge'
  },
  
  infrastructure: {
    cpu_usage: 'gauge',
    memory_usage: 'gauge',
    disk_io: 'counter',
    network_io: 'counter'
  }
};

// Custom metrics collection
const prometheus = require('prom-client');

const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const businessMetrics = new prometheus.Gauge({
  name: 'jobspy_daily_active_users',
  help: 'Number of daily active users',
  async collect() {
    const count = await db.query(`
      SELECT COUNT(DISTINCT user_id) 
      FROM api_usage 
      WHERE created_at > NOW() - INTERVAL '24 hours'
    `);
    this.set(count.rows[0].count);
  }
});
```

### Distributed Tracing

```javascript
// OpenTelemetry implementation
const opentelemetry = require('@opentelemetry/api');
const { NodeSDK } = require('@opentelemetry/auto-instrumentations-node');

const sdk = new NodeSDK({
  serviceName: 'jobspy-license-server',
  serviceVersion: process.env.APP_VERSION,
  instrumentations: [
    getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-http': {
        enabled: true,
        ignoreIncomingRequestHook: (req) => req.url === '/health'
      },
      '@opentelemetry/instrumentation-pg': { enabled: true },
      '@opentelemetry/instrumentation-redis': { enabled: true }
    })
  ]
});

// Custom spans for business logic
async function validateLicense(licenseKey, hardwareFingerprint) {
  const span = opentelemetry.trace.getActiveSpan();
  span?.setAttributes({
    'license.key': licenseKey,
    'hardware.fingerprint': hardwareFingerprint
  });
  
  const startTime = Date.now();
  try {
    const result = await licenseValidationLogic(licenseKey, hardwareFingerprint);
    span?.setStatus({ code: opentelemetry.SpanStatusCode.OK });
    return result;
  } catch (error) {
    span?.setStatus({ 
      code: opentelemetry.SpanStatusCode.ERROR,
      message: error.message 
    });
    throw error;
  } finally {
    span?.setAttributes({
      'operation.duration_ms': Date.now() - startTime
    });
  }
}
```

## Scalability Architecture

### Horizontal Scaling Strategy

```yaml
# Kubernetes deployment configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: license-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: license-server
  template:
    metadata:
      labels:
        app: license-server
    spec:
      containers:
      - name: license-server
        image: jobspy/license-server:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: license-server-service
spec:
  selector:
    app: license-server
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

### Database Scaling

```sql
-- Read replica configuration
-- Master: Write operations
-- Replica 1: Read operations (license validation)
-- Replica 2: Analytics and reporting

-- Connection routing logic
const dbConfig = {
  master: {
    host: 'master.db.jobspy.com',
    readonly: false,
    pool: { min: 5, max: 20 }
  },
  replicas: [
    {
      host: 'replica1.db.jobspy.com',
      readonly: true,
      pool: { min: 10, max: 50 }
    },
    {
      host: 'replica2.db.jobspy.com', 
      readonly: true,
      pool: { min: 5, max: 20 }
    }
  ]
};

// Automatic read/write splitting
function getDbConnection(operation) {
  if (operation === 'write') {
    return dbConfig.master;
  } else {
    const replica = dbConfig.replicas[
      Math.floor(Math.random() * dbConfig.replicas.length)
    ];
    return replica;
  }
}
```

## Documentation

### API Documentation Generation

```javascript
// Swagger/OpenAPI auto-generation
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'JobSpy License Server API',
      version: process.env.APP_VERSION,
      description: 'License validation and user management API'
    },
    servers: [
      {
        url: process.env.API_BASE_URL,
        description: 'Production server'
      }
    ]
  },
  apis: ['./routes/*.js', './models/*.js']
};

const specs = swaggerJsdoc(options);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));
```

### Architecture Decision Records (ADRs)

```markdown
# ADR-001: Database Choice - PostgreSQL vs MongoDB

## Status
Accepted

## Context
Need to choose primary database for license management and user data.

## Decision
Choose PostgreSQL over MongoDB.

## Rationale
- ACID compliance for financial transactions
- Better support for complex queries and reporting
- Mature ecosystem and operational tooling
- Strong consistency guarantees
- JSON support for flexible schema needs

## Consequences
- More complex horizontal scaling compared to MongoDB
- Need for specialized PostgreSQL expertise
- Relational modeling constraints
```

---

**Note**: This technical architecture is designed for scalability, maintainability, and performance. Each component is documented with implementation details, performance considerations, and operational procedures.