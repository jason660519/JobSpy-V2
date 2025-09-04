# System Architecture Diagrams

## Overview

This document contains visual representations of the JobSpy ecosystem architecture, including system diagrams, data flow diagrams, and deployment architecture.

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Applications"
        DA[Desktop App<br/>Electron + Python]
        BE[Browser Extension<br/>Chrome/Firefox]
        PWA[Progressive Web App<br/>Mobile/Web]
    end
    
    subgraph "API Gateway & Load Balancer"
        CF[Cloudflare<br/>CDN + DDoS Protection]
    end
    
    subgraph "Backend Services"
        LS[License Server<br/>Node.js + Express]
        PA[Premium API<br/>Python + FastAPI]
        PS[Payment Service<br/>Stripe Integration]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Primary Database)]
        RD[(Redis<br/>Cache + Sessions)]
        CH[(ClickHouse<br/>Analytics)]
    end
    
    subgraph "External Services"
        ST[Stripe<br/>Payment Processing]
        JS[Job Sites<br/>Indeed, LinkedIn, etc.]
        DS[Data Sources<br/>Salary APIs, Company APIs]
    end
    
    DA --> CF
    BE --> CF
    PWA --> CF
    
    CF --> LS
    CF --> PA
    
    LS --> PG
    LS --> RD
    PA --> PG
    PA --> RD
    PA --> CH
    
    PS --> ST
    LS --> PS
    
    PA --> DS
    DA --> JS
    BE --> JS
    
    style DA fill:#e1f5fe
    style BE fill:#e1f5fe
    style PWA fill:#e1f5fe
    style LS fill:#f3e5f5
    style PA fill:#f3e5f5
    style PS fill:#f3e5f5
    style PG fill:#fff3e0
    style RD fill:#fff3e0
    style CH fill:#fff3e0
```

## 2. Desktop Application Architecture

```mermaid
graph TB
    subgraph "Electron Main Process"
        MP[Main Process<br/>Node.js Runtime]
        IPC[IPC Communication<br/>Secure Channel]
    end
    
    subgraph "Renderer Process"
        UI[React Frontend<br/>User Interface]
        subgraph "Components"
            SC[Search Components]
            RC[Results Components]
            LC[License Components]
            SC2[Settings Components]
        end
    end
    
    subgraph "Python Backend"
        JS[JobSpy Core<br/>Python Engine]
        subgraph "Scrapers"
            IS[Indeed Scraper]
            LS2[LinkedIn Scraper]
            GS[Glassdoor Scraper]
        end
        DP[Data Processing<br/>Filtering & Export]
        FS[File System<br/>Local Storage]
    end
    
    subgraph "External Connections"
        LSV[License Server<br/>Validation]
        WSI[Job Sites<br/>Direct Access]
        PAI[Premium API<br/>Enhanced Data]
    end
    
    UI --> IPC
    IPC --> MP
    MP --> JS
    
    SC --> UI
    RC --> UI
    LC --> UI
    SC2 --> UI
    
    JS --> IS
    JS --> LS2
    JS --> GS
    JS --> DP
    JS --> FS
    
    MP --> LSV
    JS --> WSI
    MP --> PAI
    
    style MP fill:#f8bbd9
    style UI fill:#e1f5fe
    style JS fill:#fff3e0
    style DP fill:#e8f5e8
```

## 3. License Validation Flow

```mermaid
sequenceDiagram
    participant DA as Desktop App
    participant LS as License Server
    participant DB as Database
    participant RD as Redis Cache
    
    DA->>DA: Generate Hardware Fingerprint
    DA->>LS: POST /licenses/validate<br/>{license_key, hardware_fp, app_version}
    
    LS->>RD: Check cache for license_key
    alt Cache Hit
        RD->>LS: Return cached validation
        LS->>DA: Validation response
    else Cache Miss
        LS->>DB: Query license table
        DB->>LS: License record
        
        alt Valid License
            LS->>DB: Update last_validated_at
            LS->>RD: Cache validation result (1 hour)
            LS->>DA: {valid: true, license_type, features, expires_at}
        else Invalid License
            LS->>RD: Cache negative result (5 minutes)
            LS->>DA: {valid: false, reason}
        end
    end
    
    DA->>DA: Update local feature flags
```

## 4. Payment and Subscription Flow

```mermaid
sequenceDiagram
    participant U as User
    participant DA as Desktop App
    participant PS as Payment Service
    participant ST as Stripe
    participant DB as Database
    participant LS as License Server
    
    U->>DA: Click "Upgrade to Pro"
    DA->>PS: GET /pricing-plans
    PS->>DA: Available plans and prices
    
    U->>DA: Select plan and enter payment
    DA->>PS: POST /create-payment-intent
    PS->>ST: Create PaymentIntent
    ST->>PS: PaymentIntent with client_secret
    PS->>DA: client_secret
    
    DA->>ST: Confirm payment (Stripe.js)
    ST->>PS: Webhook: payment_intent.succeeded
    
    PS->>DB: Create payment record
    PS->>DB: Update user subscription
    PS->>LS: Generate new license key
    LS->>DB: Create/update license record
    
    PS->>DA: Payment confirmation
    DA->>LS: Validate new license
    LS->>DA: License validation success
    DA->>DA: Enable premium features
```

## 5. Premium Data API Flow

```mermaid
sequenceDiagram
    participant DA as Desktop App
    participant GW as API Gateway
    participant PA as Premium API
    participant RD as Redis
    participant EX as External APIs
    participant DB as Database
    
    DA->>GW: GET /premium/salary-insights<br/>Bearer token + request data
    GW->>GW: Rate limiting check
    GW->>PA: Forward request
    
    PA->>PA: Validate JWT token
    PA->>RD: Check cache for request
    
    alt Cache Hit
        RD->>PA: Return cached data
        PA->>DA: Salary insights response
    else Cache Miss
        PA->>EX: Fetch from multiple sources
        par
            PA->>EX: Glassdoor API
        and
            PA->>EX: PayScale API
        and
            PA->>EX: Salary.com API
        end
        
        EX->>PA: Raw salary data
        PA->>PA: Process and analyze data
        PA->>RD: Cache processed result (24h)
        PA->>DB: Log API usage
        PA->>DA: Salary insights response
    end
```

## 6. Data Architecture

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email UK
        string password_hash
        timestamp created_at
        timestamp updated_at
        string status
        jsonb metadata
    }
    
    LICENSES {
        uuid id PK
        uuid user_id FK
        string license_key UK
        string license_type
        string hardware_fingerprint
        string status
        timestamp expires_at
        timestamp created_at
        timestamp last_validated_at
        integer validation_count
        jsonb metadata
    }
    
    SUBSCRIPTIONS {
        uuid id PK
        uuid user_id FK
        string stripe_subscription_id UK
        string plan_type
        string status
        timestamp current_period_start
        timestamp current_period_end
        timestamp created_at
        timestamp updated_at
        jsonb metadata
    }
    
    PAYMENTS {
        uuid id PK
        uuid user_id FK
        string stripe_payment_intent_id UK
        integer amount_cents
        string currency
        string status
        string payment_method
        text description
        timestamp created_at
        jsonb metadata
    }
    
    API_USAGE {
        uuid id PK
        uuid user_id FK
        string endpoint
        string method
        integer status_code
        integer response_time_ms
        integer request_size_bytes
        integer response_size_bytes
        timestamp created_at
        jsonb metadata
    }
    
    USERS ||--o{ LICENSES : "has"
    USERS ||--o{ SUBSCRIPTIONS : "has"
    USERS ||--o{ PAYMENTS : "makes"
    USERS ||--o{ API_USAGE : "generates"
```

## 7. Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Cloudflare CDN"
            CF[Global CDN<br/>DDoS Protection<br/>SSL/TLS]
        end
        
        subgraph "Railway Platform"
            subgraph "Application Services"
                LS[License Server<br/>2 instances<br/>1GB RAM each]
                PA[Premium API<br/>3 instances<br/>2GB RAM each]
                WS[Website<br/>1 instance<br/>512MB RAM]
            end
            
            subgraph "Data Services"
                PG[(PostgreSQL<br/>Managed Database<br/>100GB SSD)]
                RD[(Redis<br/>Managed Cache<br/>4GB Memory)]
            end
        end
        
        subgraph "AWS Services"
            CH[(ClickHouse<br/>Analytics DB<br/>On EC2)]
            S3[(S3 Bucket<br/>Backups & Assets)]
            CW[CloudWatch<br/>Monitoring]
        end
        
        subgraph "External Services"
            DD[DataDog<br/>APM & Logging]
            ST[Stripe<br/>Payment Processing]
            SE[Sentry<br/>Error Tracking]
        end
    end
    
    subgraph "Client Distribution"
        GH[GitHub Releases<br/>Desktop App Binaries]
        MS[Microsoft Store<br/>Windows App]
        AS[App Store<br/>macOS App]
        CS[Chrome Store<br/>Browser Extension]
        FS[Firefox Store<br/>Browser Extension]
    end
    
    CF --> LS
    CF --> PA
    CF --> WS
    
    LS --> PG
    LS --> RD
    PA --> PG
    PA --> RD
    PA --> CH
    
    LS --> DD
    PA --> DD
    WS --> DD
    
    LS --> SE
    PA --> SE
    
    PA --> ST
    
    PG --> S3
    CH --> CW
    
    style CF fill:#ff9800
    style LS fill:#4caf50
    style PA fill:#4caf50
    style WS fill:#4caf50
    style PG fill:#2196f3
    style RD fill:#f44336
    style CH fill:#9c27b0
```

## 8. Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Network Security"
            WAF[Web Application Firewall<br/>Cloudflare]
            DDoS[DDoS Protection<br/>Cloudflare]
            TLS[TLS 1.3 Encryption<br/>All Connections]
        end
        
        subgraph "Application Security"
            JWT[JWT Token Auth<br/>RS256 Signing]
            RBAC[Role-Based Access<br/>License Tiers]
            RL[Rate Limiting<br/>Redis-based]
            IP[Input Validation<br/>Request Sanitization]
        end
        
        subgraph "Data Security"
            EAR[Encryption at Rest<br/>Database TDE]
            EIT[Encryption in Transit<br/>TLS Everywhere]
            KM[Key Management<br/>AWS Secrets Manager]
            BU[Encrypted Backups<br/>S3 with KMS]
        end
        
        subgraph "Infrastructure Security"
            VPC[Virtual Private Cloud<br/>Network Isolation]
            IAM[Identity Access Mgmt<br/>Principle of Least Privilege]
            LOG[Audit Logging<br/>All Access Tracked]
            MON[Security Monitoring<br/>SIEM Integration]
        end
    end
    
    subgraph "Compliance"
        GDPR[GDPR Compliance<br/>Data Protection]
        SOC[SOC 2 Type II<br/>Security Controls]
        PCI[PCI DSS<br/>Payment Security]
    end
    
    WAF --> DDoS
    DDoS --> TLS
    TLS --> JWT
    JWT --> RBAC
    RBAC --> RL
    RL --> IP
    
    EAR --> EIT
    EIT --> KM
    KM --> BU
    
    VPC --> IAM
    IAM --> LOG
    LOG --> MON
    
    style WAF fill:#f44336
    style JWT fill:#ff9800
    style EAR fill:#4caf50
    style VPC fill:#2196f3
    style GDPR fill:#9c27b0
```

## 9. Monitoring Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        APP[Applications<br/>License Server<br/>Premium API]
        LOGS[Application Logs<br/>Structured JSON]
        METRICS[Custom Metrics<br/>Business KPIs]
        TRACES[Distributed Traces<br/>OpenTelemetry]
    end
    
    subgraph "Infrastructure Layer"
        INFRA[Infrastructure<br/>Railway Platform<br/>AWS Services]
        SYS[System Metrics<br/>CPU, Memory, Disk]
        NET[Network Metrics<br/>Latency, Throughput]
    end
    
    subgraph "Monitoring Platform"
        DD[DataDog<br/>APM & Infrastructure]
        PROM[Prometheus<br/>Metrics Collection]
        GRAF[Grafana<br/>Dashboards]
        ALERT[AlertManager<br/>Notifications]
    end
    
    subgraph "Notification Channels"
        SLACK[Slack<br/>Team Notifications]
        EMAIL[Email<br/>Critical Alerts]
        PHONE[Phone/SMS<br/>Emergency Escalation]
        TICKET[PagerDuty<br/>Incident Management]
    end
    
    APP --> LOGS
    APP --> METRICS
    APP --> TRACES
    
    INFRA --> SYS
    INFRA --> NET
    
    LOGS --> DD
    METRICS --> PROM
    TRACES --> DD
    SYS --> DD
    NET --> DD
    
    PROM --> GRAF
    DD --> ALERT
    GRAF --> ALERT
    
    ALERT --> SLACK
    ALERT --> EMAIL
    ALERT --> PHONE
    ALERT --> TICKET
    
    style APP fill:#4caf50
    style DD fill:#ff6b6b
    style ALERT fill:#ffa726
    style SLACK fill:#4a154b
```

## 10. Scalability Architecture

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        subgraph "Load Balancers"
            ALB[Application Load Balancer<br/>Railway/AWS]
            CF[Cloudflare<br/>Global Load Balancing]
        end
        
        subgraph "Application Tier"
            LS1[License Server 1]
            LS2[License Server 2]
            LS3[License Server N]
            
            PA1[Premium API 1]
            PA2[Premium API 2]
            PA3[Premium API N]
        end
        
        subgraph "Data Tier"
            MASTER[(PostgreSQL Master<br/>Write Operations)]
            REPLICA1[(Read Replica 1<br/>License Validation)]
            REPLICA2[(Read Replica 2<br/>Analytics)]
            
            REDIS1[(Redis Cluster 1<br/>Sessions & Cache)]
            REDIS2[(Redis Cluster 2<br/>Rate Limiting)]
        end
    end
    
    subgraph "Vertical Scaling"
        AUTO[Auto-scaling<br/>Based on Metrics]
        CPU[CPU Utilization > 70%]
        MEM[Memory Usage > 80%]
        RESP[Response Time > 2s]
    end
    
    CF --> ALB
    ALB --> LS1
    ALB --> LS2
    ALB --> LS3
    ALB --> PA1
    ALB --> PA2
    ALB --> PA3
    
    LS1 --> MASTER
    LS2 --> REPLICA1
    LS3 --> REPLICA1
    
    PA1 --> MASTER
    PA2 --> REPLICA2
    PA3 --> REPLICA2
    
    LS1 --> REDIS1
    PA1 --> REDIS2
    
    AUTO --> CPU
    AUTO --> MEM
    AUTO --> RESP
    
    style AUTO fill:#ff9800
    style MASTER fill:#4caf50
    style REPLICA1 fill:#81c784
    style REPLICA2 fill:#81c784
```

---

**Note**: These diagrams provide a comprehensive visual overview of the JobSpy ecosystem architecture. They can be rendered using any Mermaid-compatible tool or online editors like mermaid.live or draw.io.