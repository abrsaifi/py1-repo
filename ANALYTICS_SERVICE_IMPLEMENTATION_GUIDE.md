# Analytics Service - Historical Implementation Guide

This guide documents the earlier target analytics-service split.
In the current workspace, the active backend runtime is the modular Flask application under `app/`, so the analytics-service deployment and startup steps below should be treated as historical or reference material unless the repository is intentionally re-split.

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [API Reference](#api-reference)
5. [Metrics Definitions](#metrics-definitions)
6. [Processors & Business Logic](#processors--business-logic)
7. [Setup & Installation](#setup--installation)
8. [Configuration](#configuration)
9. [Usage Examples](#usage-examples)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)
12. [Performance Tuning](#performance-tuning)

---

## Overview

The Analytics Service was designed as a standalone microservice component of the SaaS platform that provides comprehensive business intelligence, user engagement tracking, revenue analytics, and predictive analytics capabilities.

**Service Port**: 5005
**Language**: Python 3.9+
**Framework**: Flask
**Database**: PostgreSQL
**Cache**: Redis

### Key Capabilities

- **Daily User Metrics**: Conversion tracking, file processing, performance metrics
- **Revenue Metrics**: MRR, ARR, ARPU, churn rate, expansion metrics
- **User Engagement**: Health scoring, lifecycle tracking, feature adoption
- **Conversion Analytics**: Format-specific analysis, success rates, performance
- **Custom Events**: Flexible event tracking with categories and properties
- **Reporting**: Scheduled report generation with multiple report types
- **Dashboards**: Custom, shareable dashboards with widgets
- **Churn Prediction**: ML-based risk assessment with contributing factors
- **Funnel Analysis**: Customer journey tracking (signup → expansion → churn)
- **Cohort Analysis**: Retention metrics by user cohort

---

## Architecture

### Service Components

```
analytics-service/
├── main.py                 # Flask app & core endpoints (700 lines)
├── endpoints.py            # Advanced analytics endpoints (1000 lines)
├── processors.py           # Business logic & ML models (1200 lines)
├── test_analytics_service.py  # Comprehensive tests (900 lines)
└── requirements.txt        # Python dependencies
```

### Integration with Other Services

```
┌─────────────────────────┐
│   API Gateway (5000)    │
└────────────┬────────────┘
             │
             ├─► Auth Service (5001)
             ├─► User Service (5002)
             ├─► Conversion Service (5003)
             ├─► Billing Service (5004)
             └─► Analytics Service (5005) ◄─── THIS SERVICE
                        │
                        ├─► PostgreSQL (events, metrics)
                        └─► Redis (caching)
```

### Data Flow

1. **Event Generation**: Services create custom events (conversions, signups, payments)
2. **Event Aggregation**: Analytics Service collects and aggregates events
3. **Metric Calculation**: Daily/monthly metrics computed from events
4. **Prediction**: ML models assess churn risk based on engagement patterns
5. **Reporting**: Scheduled reports generated from calculated metrics
6. **Caching**: Frequently accessed metrics cached in Redis

---

## Database Schema

### Core Models

#### 1. DailyMetric
Aggregate metrics per user per day

```sql
CREATE TABLE daily_metrics (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    date DATE NOT NULL,
    
    -- Conversion metrics
    conversions INTEGER DEFAULT 0,
    successful_conversions INTEGER DEFAULT 0,
    failed_conversions INTEGER DEFAULT 0,
    
    -- File metrics
    input_bytes BIGINT DEFAULT 0,
    output_bytes BIGINT DEFAULT 0,
    
    -- Processing metrics
    total_processing_seconds FLOAT DEFAULT 0,
    avg_processing_seconds FLOAT DEFAULT 0,
    peak_concurrent_jobs INTEGER DEFAULT 0,
    
    -- Format breakdown (JSON)
    format_usage JSON DEFAULT '{}',
    
    -- Feature tracking (JSON)
    features_used JSON DEFAULT '{}',
    
    -- API metrics
    api_calls INTEGER DEFAULT 0,
    api_errors INTEGER DEFAULT 0,
    
    -- Session tracking
    sessions INTEGER DEFAULT 0,
    session_duration_seconds INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_user_date (user_id, date)
);
```

**Use Cases**:
- Daily conversion trends
- Processing performance analysis
- Format usage breakdown
- Session duration tracking

#### 2. RevenueMetric
Monthly business metrics

```sql
CREATE TABLE revenue_metrics (
    id VARCHAR(36) PRIMARY KEY,
    year_month VARCHAR(7) NOT NULL UNIQUE,  -- YYYY-MM
    
    -- MRR/ARR
    mrr_cents BIGINT,           -- Monthly recurring revenue
    arr_cents BIGINT,           -- Annual recurring revenue
    total_revenue_cents BIGINT,
    
    -- Subscription counts
    active_subscriptions INTEGER,
    new_subscriptions INTEGER,
    cancelled_subscriptions INTEGER,
    net_new_subscriptions INTEGER,
    
    -- Tier breakdown
    free_tier_count INTEGER DEFAULT 0,
    starter_tier_count INTEGER DEFAULT 0,
    pro_tier_count INTEGER DEFAULT 0,
    enterprise_tier_count INTEGER DEFAULT 0,
    
    -- Key metrics
    arpu_cents INTEGER,         -- Average revenue per user
    customer_count INTEGER,
    paying_customers INTEGER,
    
    -- Churn metrics
    churn_count INTEGER,
    churn_rate FLOAT,           -- Percentage
    
    -- Expansion
    upgrades INTEGER DEFAULT 0,
    downgrades INTEGER DEFAULT 0,
    expansion_revenue_cents BIGINT DEFAULT 0,
    
    INDEX idx_year_month (year_month)
);
```

**Use Cases**:
- Monthly revenue reporting
- Subscription growth tracking
- Churn analysis
- Tier distribution

#### 3. UserMetric
User engagement and lifecycle

```sql
CREATE TABLE user_metrics (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    
    -- Sessions
    total_sessions INTEGER DEFAULT 0,
    session_duration_seconds BIGINT DEFAULT 0,
    last_activity_date DATE,
    
    -- Lifecycle
    days_since_signup INTEGER,
    subscription_duration_days INTEGER,
    
    -- Usage
    total_conversions INTEGER DEFAULT 0,
    total_api_calls INTEGER DEFAULT 0,
    
    -- Subscription history
    current_subscription VARCHAR(50),
    times_upgraded INTEGER DEFAULT 0,
    times_downgraded INTEGER DEFAULT 0,
    
    -- Feature adoption
    features_used JSON DEFAULT '{}',
    feature_count INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive, churned
    lifecycle_stage VARCHAR(50),          -- free, trial, subscriber, churned
    
    -- Health scoring (0-100)
    health_score INTEGER DEFAULT 50,
    
    -- Satisfaction
    nps_score INTEGER,          -- -100 to 100
    satisfaction_rating INTEGER, -- 1-5
    
    INDEX idx_user_id (user_id)
);
```

**Use Cases**:
- User engagement scoring
- Lifecycle stage tracking
- Feature adoption analysis
- Health-based segmentation

#### 4. ConversionAnalytic
Format-specific conversion metrics

```sql
CREATE TABLE conversion_analytics (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    month VARCHAR(7) NOT NULL,  -- YYYY-MM
    
    -- Conversions
    total_conversions INTEGER,
    successful_conversions INTEGER,
    failed_conversions INTEGER,
    success_rate FLOAT,         -- Percentage
    
    -- Format breakdown
    pdf_conversions INTEGER DEFAULT 0,
    docx_conversions INTEGER DEFAULT 0,
    image_conversions INTEGER DEFAULT 0,
    video_conversions INTEGER DEFAULT 0,
    other_conversions INTEGER DEFAULT 0,
    
    -- Performance
    avg_processing_time_seconds FLOAT,
    median_processing_time_seconds FLOAT,
    max_processing_time_seconds FLOAT,
    
    -- Data volume
    total_input_mb BIGINT,
    total_output_mb BIGINT,
    avg_file_size_mb FLOAT,
    
    -- Errors (JSON)
    common_errors JSON DEFAULT '{}',
    
    INDEX idx_user_month (user_id, month)
);
```

**Use Cases**:
- Format-specific performance analysis
- Success rate by format
- Data volume tracking
- Error pattern identification

#### 5. CustomEvent
Flexible event tracking system

```sql
CREATE TABLE custom_events (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    
    -- Event classification
    category VARCHAR(50) NOT NULL,     -- USER_ACTION, CONVERSION, PAYMENT, etc.
    event_type VARCHAR(100) NOT NULL,
    event_name VARCHAR(255),
    
    -- Event data
    properties JSON,
    value FLOAT,
    
    -- Session tracking
    session_id VARCHAR(36),
    
    -- Client info
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at),
    INDEX idx_user_category_type (user_id, category, event_type)
);
```

**Event Categories**:
- `USER_ACTION`: Feature usage, page views
- `CONVERSION`: File conversions, exports
- `PAYMENT`: Subscription changes, payments
- `SUBSCRIPTION`: Signup, upgrade, downgrade, churn
- `ERROR`: API errors, conversion failures
- `PERFORMANCE`: Processing time, resource usage
- `SYSTEM`: Health checks, maintenance
- `CUSTOM`: Application-specific events

#### 6. Report
Scheduled report generation and delivery

```sql
CREATE TABLE reports (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    
    -- Report metadata
    name VARCHAR(255),
    report_type VARCHAR(50),      -- DAILY, WEEKLY, MONTHLY, etc.
    title VARCHAR(255),
    description TEXT,
    
    -- Status
    status VARCHAR(50),           -- SCHEDULED, GENERATING, COMPLETED, FAILED
    
    -- Scheduling
    is_scheduled BOOLEAN DEFAULT FALSE,
    cron_expression VARCHAR(255), -- "0 9 * * MON" format
    
    -- Configuration
    metrics JSON,                 -- Array of metric names
    filters JSON,                 -- Filter criteria
    
    -- Content and delivery
    generated_content JSON,
    email_recipients JSON,        -- Array of email addresses
    
    -- Dates
    scheduled_date TIMESTAMP,
    generated_date TIMESTAMP,
    next_run_date TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_report_type (user_id, report_type)
);
```

#### 7. Dashboard
Custom, shareable dashboards

```sql
CREATE TABLE dashboards (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    
    -- Dashboard metadata
    name VARCHAR(255),
    description TEXT,
    
    -- Configuration
    widgets JSON,                 -- Array of widget definitions
    layout JSON,                  -- Grid layout info
    
    -- Sharing
    is_public BOOLEAN DEFAULT FALSE,
    is_shared BOOLEAN DEFAULT FALSE,
    shared_with JSON,             -- Array of user IDs
    
    -- Preferences
    refresh_interval_minutes INTEGER DEFAULT 5,
    theme VARCHAR(50) DEFAULT 'light',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id)
);
```

#### 8. FunnelAnalysis
Customer journey tracking

```sql
CREATE TABLE funnel_analysis (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    
    -- Stage tracking
    current_stage VARCHAR(50),    -- SIGNUP, TRIAL, CONVERSION, SUBSCRIPTION, EXPANSION, CHURN
    stages_completed INTEGER DEFAULT 0,
    
    -- Completion dates
    signup_at TIMESTAMP,
    trial_start_at TIMESTAMP,
    trial_end_at TIMESTAMP,
    first_conversion_at TIMESTAMP,
    subscription_at TIMESTAMP,
    first_expansion_at TIMESTAMP,
    churn_at TIMESTAMP,
    
    -- Conversion metrics
    trial_to_paid_conversion BOOLEAN,
    
    -- Timing metrics (in days)
    trial_duration_days INTEGER,
    days_to_first_conversion INTEGER,
    days_to_subscription INTEGER,
    days_to_expansion INTEGER,
    
    INDEX idx_user_stage (user_id, current_stage)
);
```

#### 9. CohortAnalysis
User retention by cohort

```sql
CREATE TABLE cohort_analysis (
    id VARCHAR(36) PRIMARY KEY,
    cohort_month VARCHAR(7) NOT NULL,  -- YYYY-MM
    cohort_name VARCHAR(255),
    
    -- Cohort size
    users_in_cohort INTEGER,
    
    -- Retention counts (raw user counts)
    month_0_users INTEGER,
    month_1_users INTEGER,
    month_2_users INTEGER,
    month_3_users INTEGER,
    month_6_users INTEGER,
    month_12_users INTEGER,
    
    -- Retention rates (percentages)
    month_1_retention FLOAT,
    month_2_retention FLOAT,
    month_3_retention FLOAT,
    month_6_retention FLOAT,
    month_12_retention FLOAT,
    
    -- Revenue
    month_0_revenue_cents BIGINT,
    month_1_revenue_cents BIGINT,
    total_revenue_cents BIGINT,
    
    INDEX idx_cohort_month (cohort_month)
);
```

#### 10. ChurnPrediction
ML-based churn risk modeling

```sql
CREATE TABLE churn_predictions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    
    -- Prediction
    churn_probability FLOAT,      -- 0.0 to 1.0
    churn_risk_level VARCHAR(20), -- LOW, MEDIUM, HIGH, CRITICAL
    predicted_churn_date TIMESTAMP,
    
    -- Contributing factors
    contributing_factors JSON,
    recommended_action TEXT,
    recommended_offer TEXT,
    
    -- Action tracking
    action_taken BOOLEAN DEFAULT FALSE,
    action_description TEXT,
    
    -- Results
    actual_churned BOOLEAN,
    is_prediction_accurate BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id)
);
```

#### 11. AnalyticsCache
Performance caching with TTL

```sql
CREATE TABLE analytics_cache (
    id VARCHAR(36) PRIMARY KEY,
    cache_key VARCHAR(255) NOT NULL UNIQUE,
    metric_type VARCHAR(100),
    
    -- User/date context
    user_id VARCHAR(36),
    date_range_start DATE,
    date_range_end DATE,
    
    -- Cached data
    cached_data JSON,
    
    -- Cache control
    ttl_minutes INTEGER DEFAULT 60,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_cache_key (cache_key),
    INDEX idx_expires_at (expires_at)
);
```

---

## API Reference

### Authentication

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

Admin-only endpoints require `X-Admin-Key: admin` header.

### Daily Metrics Endpoints

#### GET /analytics/daily-metrics
Get user's daily metrics

**Parameters**:
- `date` (optional): Target date (ISO format, default: today)
- `days` (optional): Number of days to retrieve (default: 1)

**Response**:
```json
{
    "metrics": [
        {
            "id": "uuid",
            "user_id": "uuid",
            "date": "2024-01-15",
            "conversions": 5,
            "successful_conversions": 4,
            "input_bytes": 1024000,
            "output_bytes": 2048000,
            "format_usage": {"pdf": 3, "docx": 2},
            "sessions": 2
        }
    ],
    "count": 15,
    "date_range": {"start": "2024-01-01", "end": "2024-01-15"}
}
```

#### GET /analytics/user-metrics
Get user engagement metrics and health score

**Response**:
```json
{
    "id": "uuid",
    "user_id": "uuid",
    "total_sessions": 25,
    "total_conversions": 8,
    "health_score": 78,
    "lifecycle_stage": "subscriber",
    "days_since_signup": 45,
    "subscription_duration_days": 30,
    "nps_score": 45,
    "satisfaction_rating": 4
}
```

### Revenue Metrics Endpoints (Admin)

#### GET /analytics/revenue-metrics
Get platform revenue metrics

**Parameters**:
- `months` (optional): Number of months to retrieve (default: 12, max: 24)

**Response**:
```json
{
    "metrics": [
        {
            "year_month": "2024-01",
            "mrr_cents": 50000,
            "arr_cents": 600000,
            "arpu_cents": 5000,
            "churn_rate": 2.5,
            "active_subscriptions": 100,
            "new_subscriptions": 15,
            "cancelled_subscriptions": 2,
            "expansion_revenue_cents": 5000
        }
    ],
    "count": 12,
    "aggregates": {
        "total_revenue_cents": 600000,
        "avg_mrr_cents": 50000
    }
}
```

### Custom Events Endpoints

#### POST /analytics/events
Track a custom event

**Request**:
```json
{
    "event_type": "feature_used",
    "event_name": "OCR Feature Activated",
    "category": "user_action",
    "properties": {
        "source": "dashboard",
        "duration_seconds": 45,
        "success": true
    },
    "value": 1.5
}
```

**Response**:
```json
{
    "success": true,
    "event": {
        "id": "uuid",
        "user_id": "uuid",
        "event_type": "feature_used",
        "category": "user_action",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

#### GET /analytics/events
Get user's events

**Parameters**:
- `event_type` (optional): Filter by event type
- `limit` (optional): Max results (default: 50, max: 100)

**Response**:
```json
{
    "events": [
        {
            "id": "uuid",
            "event_type": "feature_used",
            "event_name": "OCR Feature",
            "category": "user_action",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "count": 45
}
```

### Dashboard Endpoints

#### GET /analytics/dashboards
List user's dashboards

**Response**:
```json
{
    "dashboards": [
        {
            "id": "uuid",
            "name": "Executive Dashboard",
            "description": "High-level KPIs",
            "widgets": [...],
            "is_public": false,
            "refresh_interval_minutes": 5
        }
    ],
    "count": 3
}
```

#### POST /analytics/dashboards
Create new dashboard

**Request**:
```json
{
    "name": "Custom Dashboard",
    "description": "My metrics",
    "widgets": [
        {
            "id": "widget-1",
            "type": "daily_conversions",
            "title": "Daily Conversions",
            "config": {}
        }
    ]
}
```

#### GET /analytics/dashboards/{dashboard_id}
Get dashboard details

#### PUT /analytics/dashboards/{dashboard_id}
Update dashboard

### Report Endpoints

#### GET /analytics/reports
List user's reports

**Parameters**:
- `report_type` (optional): Filter by type (daily, weekly, monthly, etc.)

#### POST /analytics/reports/generate
Generate on-demand report

**Request**:
```json
{
    "report_type": "monthly",
    "metrics": ["conversions", "revenue", "churn_rate"],
    "filters": {
        "date_range": "last_month",
        "min_activity": 1
    }
}
```

#### POST /analytics/reports/{report_id}/schedule
Schedule recurring report

**Request**:
```json
{
    "cron_expression": "0 9 * * MON",
    "email_recipients": ["user@example.com", "manager@example.com"]
}
```

### Funnel Endpoints

#### GET /analytics/funnel/stages
Get user's funnel stage

**Response**:
```json
{
    "current_stage": "subscription",
    "stages_completed": 4,
    "trial_to_paid_conversion": true,
    "timing": {
        "trial_duration_days": 7,
        "days_to_first_conversion": 3,
        "days_to_subscription": 0,
        "days_to_expansion": null
    }
}
```

#### GET /analytics/funnel/conversion-rate (Admin)
Get platform funnel conversion rates

**Response**:
```json
{
    "total_users": 1000,
    "stage_distribution": {
        "signup": 1000,
        "trial": 450,
        "conversion": 200,
        "subscription": 180,
        "expansion": 45
    },
    "conversion_rates": {
        "signup_to_trial": 45.0,
        "trial_to_subscription": 40.0,
        "subscription_to_expansion": 25.0
    }
}
```

### Churn Endpoints

#### GET /analytics/churn-risk
Get user's churn risk assessment

**Response**:
```json
{
    "user_id": "uuid",
    "churn_probability": 0.35,
    "churn_risk_level": "medium",
    "predicted_churn_date": "2024-03-15",
    "contributing_factors": {
        "inactivity_risk": {
            "weight": 0.20,
            "days_inactive": 25,
            "value": 0.83
        },
        "low_engagement": {
            "weight": 0.15,
            "sessions": 3,
            "value": 0.4
        }
    },
    "recommended_action": "Send re-engagement email",
    "recommended_offer": "10% discount offer"
}
```

#### GET /analytics/churn-predictions (Admin)
Get high-risk users

**Parameters**:
- `risk_level` (optional): Filter by 'high' or 'critical' (default: all)
- `limit` (optional): Max results (default: 50)

---

## Metrics Definitions

### Daily Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `conversions` | Integer | Total conversions for the day |
| `successful_conversions` | Integer | Successful file conversions |
| `failed_conversions` | Integer | Failed conversions |
| `input_bytes` | Integer | Total input file bytes |
| `output_bytes` | Integer | Total output file bytes |
| `total_processing_seconds` | Float | Sum of processing time |
| `avg_processing_seconds` | Float | Average processing time per conversion |
| `format_usage` | JSON | Breakdown by format (PDF, DOCX, etc.) |
| `sessions` | Integer | Number of sessions |
| `api_calls` | Integer | API calls made |

### Revenue Metrics

| Metric | Type | Description | Formula |
|--------|------|-------------|---------|
| `mrr_cents` | Integer | Monthly Recurring Revenue | Sum of monthly subscriptions |
| `arr_cents` | Integer | Annual Recurring Revenue | MRR × 12 |
| `arpu_cents` | Integer | Avg Revenue Per User | Total Revenue / Active Users |
| `churn_rate` | Float | Monthly churn percentage | (Cancelled / Starting Active) × 100 |
| `ltv_cents` | Integer | Lifetime Value | ARPU / Monthly Churn Rate |
| `cac_cents` | Integer | Customer Acquisition Cost | Total Marketing / New Customers |

### User Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `health_score` | 0-100 | Overall user health (engagement + retention) |
| `lifecycle_stage` | Enum | free → trial → subscriber → expansion → churn |
| `nps_score` | -100 to 100 | Net Promoter Score |
| `satisfaction_rating` | 1-5 | User satisfaction score |
| `days_since_signup` | Integer | Days since account creation |

### Churn Risk Factors

| Factor | Weight | Range | Description |
|--------|--------|-------|-------------|
| Inactivity | 20% | 0-1.0 | Days since last activity |
| Low Health Score | 25% | 0-1.0 | Health score below 40 |
| Low Engagement | 15% | 0-1.0 | Sessions < 5 |
| Declining Usage | 15% | 0-1.0 | Week usage < 30% of month |
| Subscription Risk | 25% | 0-1.0 | Billing failures or disputes |

---

## Processors & Business Logic

### MetricsCalculator

Aggregates raw data into meaningful metrics.

**Methods**:
- `calculate_daily_metrics(user_id, date)` - Daily aggregation
- `calculate_monthly_revenue(year_month)` - Revenue rollup
- `calculate_user_metrics(user_id)` - Engagement scoring

**Processing Logic**:
1. Query all events for time period
2. Aggregate by category and format
3. Calculate averages and rates
4. Update metric records
5. Invalidate related caches

### ChurnPredictor

ML-based churn risk assessment.

**Algorithm**:
1. Base probability: 0.10 (10%)
2. Add weight for each risk factor:
   - Inactivity (>30 days): +0.20
   - Low health (<40): +0.25
   - Low engagement (<5 sessions): +0.15
   - Declining usage (week < 30% of month): +0.15
3. Cap at 0.95 (95%)
4. Classify risk level:
   - LOW: 0-20%
   - MEDIUM: 20-50%
   - HIGH: 50-80%
   - CRITICAL: 80%+
5. Generate recommendations based on risk

### AnalyticsCacher

Redis-based caching for performance.

**Cache Strategies**:
- `user_metrics`: 30 min TTL
- `daily_metrics`: 1 hour TTL
- `revenue_metrics`: 24 hours TTL
- Invalidation on data updates

### FunnelAnalyzer

Customer journey tracking.

**Funnel Stages**:
1. SIGNUP - Account created
2. TRIAL - Trial period started
3. CONVERSION - First conversion completed
4. SUBSCRIPTION - Paid subscription active
5. EXPANSION - Additional tier purchased
6. CHURN - Account cancelled

**Timing Metrics**:
- Trial duration (days)
- Time to first conversion (days)
- Time to subscription (days)
- Time to expansion (days)

### CohortAnalyzer

Retention analysis by cohort.

**Retention Calculation**:
- Month 0: Cohort creation
- Month 1: % still active after 30 days
- Month 3: % still active after 90 days
- Month 6: % still active after 180 days
- Month 12: % still active after 365 days

### ReportGenerator

Report generation and delivery.

**Report Types**:
1. DAILY - Daily metrics snapshot
2. WEEKLY - Week-over-week trends
3. MONTHLY - Monthly comprehensive report
4. QUARTERLY - Quarterly business review
5. YEARLY - Annual summary
6. CUSTOM - User-defined report

---

## Setup & Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- pip

### Installation Steps

```bash
# 1. Navigate to service directory
cd services/analytics-service

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export DATABASE_URL=postgresql://user:password@localhost:5432/saas_db
export REDIS_HOST=localhost
export REDIS_PORT=6379
export JWT_SECRET_KEY=your-secret-key
export ENV=development

# 5. Run migrations
python -c "from packages.shared_models.postgres_manager import PostgresDatabase; db = PostgresDatabase(); db.init(os.getenv('DATABASE_URL')); db.create_all_tables()"

# 6. Start service
python main.py
```

### Docker Setup

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=5005

EXPOSE 5005

CMD ["python", "main.py"]
```

**Docker Compose**:
```yaml
analytics-service:
  build:
    context: ./services/analytics-service
  ports:
    - "5005:5005"
  environment:
    DATABASE_URL: postgresql://user:password@postgres:5432/saas_db
    REDIS_HOST: redis
    REDIS_PORT: 6379
    JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    ENV: production
  depends_on:
    - postgres
    - redis
  networks:
    - saas_network
```

---

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/saas_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=       # Optional
REDIS_DB=1

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Service
ENV=development       # development, staging, production
PORT=5005
WORKERS=4             # For production

# External Services
AUTH_SERVICE_URL=http://localhost:5001
USER_SERVICE_URL=http://localhost:5002
CONVERSION_SERVICE_URL=http://localhost:5003
BILLING_SERVICE_URL=http://localhost:5004

# Reporting
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Analytics
CHURN_PREDICTION_INTERVAL_HOURS=6
REPORT_GENERATION_INTERVAL_HOURS=1
CACHE_TTL_MINUTES=60
```

### Configuration File

Create `config.yml`:
```yaml
development:
  debug: true
  testing: false
  json_sort_keys: false

staging:
  debug: false
  testing: false

production:
  debug: false
  testing: false
  workers: 8
  max_content_length: 52428800
```

---

## Usage Examples

### Example 1: Track User Event

```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

event = {
    'event_type': 'conversion_completed',
    'event_name': 'PDF Conversion Completed',
    'category': 'conversion',
    'properties': {
        'format': 'pdf',
        'success': True,
        'processing_time': 2.5,
        'input_bytes': 1024000,
        'output_bytes': 2048000
    },
    'value': 1.0
}

response = requests.post(
    'http://localhost:5005/analytics/events',
    json=event,
    headers=headers
)

print(response.json())
```

### Example 2: Get Daily Metrics

```python
import requests

headers = {'Authorization': f'Bearer {token}'}

# Get last 30 days
response = requests.get(
    'http://localhost:5005/analytics/daily-metrics?days=30',
    headers=headers
)

metrics = response.json()
for m in metrics['metrics']:
    print(f"{m['date']}: {m['conversions']} conversions")
```

### Example 3: Create Custom Dashboard

```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

dashboard = {
    'name': 'Executive Dashboard',
    'description': 'Top-level KPIs',
    'widgets': [
        {
            'type': 'daily_conversions',
            'title': 'Daily Conversions',
            'config': {'days': 7}
        },
        {
            'type': 'health_score',
            'title': 'Team Health',
            'config': {}
        },
        {
            'type': 'churn_risk',
            'title': 'At-Risk Users',
            'config': {}
        }
    ]
}

response = requests.post(
    'http://localhost:5005/analytics/dashboards',
    json=dashboard,
    headers=headers
)

dashboard_id = response.json()['dashboard']['id']
print(f"Created dashboard: {dashboard_id}")
```

### Example 4: Schedule Monthly Report

```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# First, generate report
report_data = {
    'report_type': 'monthly',
    'metrics': ['conversions', 'revenue', 'churn', 'health_score']
}

response = requests.post(
    'http://localhost:5005/analytics/reports/generate',
    json=report_data,
    headers=headers
)

report_id = response.json()['report']['id']

# Then schedule it
schedule = {
    'cron_expression': '0 9 1 * *',  # 9 AM on first of month
    'email_recipients': ['team@example.com', 'ceo@example.com']
}

response = requests.post(
    f'http://localhost:5005/analytics/reports/{report_id}/schedule',
    json=schedule,
    headers=headers
)

print(f"Report scheduled: {response.json()}")
```

### Example 5: Get Churn Risk Assessment

```python
import requests

headers = {'Authorization': f'Bearer {token}'}

response = requests.get(
    'http://localhost:5005/analytics/churn-risk',
    headers=headers
)

churn = response.json()

if churn['churn_probability'] > 0.5:
    print(f"⚠️ High risk: {churn['churn_probability']*100:.1f}%")
    print(f"Recommendation: {churn['recommended_action']}")
    print(f"Offer: {churn['recommended_offer']}")
```

---

## Deployment

### Production Deployment

#### 1. Application Server (Gunicorn)

```bash
pip install gunicorn

gunicorn \
    --workers 8 \
    --worker-class sync \
    --bind 0.0.0.0:5005 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    main:app
```

#### 2. Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name analytics-service;

    location / {
        proxy_pass http://localhost:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeouts for long-running queries
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Health check
    location /analytics/health {
        proxy_pass http://localhost:5005/analytics/health;
    }
}
```

#### 3. Systemd Service

Create `/etc/systemd/system/analytics-service.service`:
```ini
[Unit]
Description=Analytics Service
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=appuser
ExecStart=/usr/bin/gunicorn \
    --workers 8 \
    --bind 127.0.0.1:5005 \
    --timeout 120 \
    main:app
WorkingDirectory=/opt/saas/services/analytics-service
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

### Monitoring & Alerting

Create `/opt/monitoring/analytics-rules.yml`:
```yaml
groups:
  - name: analytics_service
    rules:
      - alert: AnalyticsServiceDown
        expr: up{job="analytics-service"} == 0
        for: 2m
        annotations:
          summary: "Analytics Service is down"

      - alert: HighChurnPredictionLatency
        expr: histogram_quantile(0.95, analytics_request_duration_seconds) > 5
        for: 5m
        annotations:
          summary: "Churn prediction queries taking too long"

      - alert: DatabaseConnectionPoolExhausted
        expr: db_pool_checked_out_connections > 20
        for: 5m
        annotations:
          summary: "Database connection pool exhausted"

      - alert: RedisCacheMissRate
        expr: rate(cache_misses[5m]) > 0.2
        for: 5m
        annotations:
          summary: "Redis cache miss rate too high"
```

---

## Troubleshooting

### Issue: High Latency on Churn Prediction

**Symptom**: Churn risk endpoint takes >5 seconds

**Solutions**:
1. Check cache hit rate:
   ```python
   redis.info('stats')['hits']
   ```
2. Add database indexes:
   ```sql
   CREATE INDEX idx_user_metric_lookup ON user_metrics(user_id);
   CREATE INDEX idx_daily_metric_lookup ON daily_metrics(user_id, date DESC);
   ```
3. Increase Redis TTL:
   ```python
   CACHE_TTL_USER = 3600  # Increase from 1800
   ```

### Issue: Reports Never Complete

**Symptom**: Report status stays "GENERATING"

**Solutions**:
1. Check for stuck processes:
   ```sql
   SELECT * FROM reports WHERE status = 'GENERATING' AND updated_at < NOW() - INTERVAL '1 hour';
   ```
2. Increase worker timeouts:
   ```bash
   export CELERY_SOFT_TIMELIMIT=300
   export CELERY_HARD_TIMELIMIT=600
   ```
3. Check logs for errors:
   ```bash
   tail -f /var/log/analytics-service/error.log
   ```

### Issue: Memory Leaks in Cache

**Symptom**: Redis memory grows indefinitely

**Solutions**:
1. Set max memory policy:
   ```bash
   redis-cli CONFIG SET maxmemory-policy allkeys-lru
   ```
2. Monitor cache expiration:
   ```python
   redis.info('stats')['evicted_keys']
   ```
3. Implement cache invalidation on updates:
   ```python
   @app.after_request
   def invalidate_cache(response):
       if response.status_code in [200, 201, 204]:
           redis.delete(f"user_metrics:{user_id}")
       return response
   ```

### Issue: Timezone Inconsistencies

**Symptom**: Metrics show wrong dates

**Solutions**:
1. Set service timezone:
   ```bash
   export TZ=UTC
   ```
2. Always use UTC for timestamps:
   ```python
   from datetime import datetime, timezone
   now = datetime.now(timezone.utc)
   ```
3. Check database timezone:
   ```sql
   SHOW timezone;  -- Should be UTC
   ```

---

## Performance Tuning

### Database Optimization

```sql
-- Create covering indexes
CREATE INDEX idx_daily_metrics_covering 
  ON daily_metrics(user_id, date DESC) 
  INCLUDE (conversions, successful_conversions);

-- Analyze query plans
EXPLAIN ANALYZE SELECT * FROM daily_metrics 
WHERE user_id = 'xyz' AND date >= '2024-01-01';

-- Partition large tables
CREATE TABLE daily_metrics_2024_q1 PARTITION OF daily_metrics
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

### Query Optimization

```python
# Bad: N+1 query
for metric in daily_metrics:
    user = User.query.get(metric.user_id)

# Good: Eager loading
metrics = session.query(DailyMetric).options(
    joinedload(DailyMetric.user)
).all()

# Bad: SELECT *
SELECT * FROM daily_metrics WHERE user_id = 'xyz';

# Good: Select specific columns
SELECT conversions, date FROM daily_metrics WHERE user_id = 'xyz';
```

### Caching Strategy

```python
# Multi-level caching
def get_daily_metrics(user_id, date):
    # Level 1: Local memory cache (5 min)
    if user_id in LOCAL_CACHE and cache_age < 300:
        return LOCAL_CACHE[user_id]
    
    # Level 2: Redis (1 hour)
    redis_key = f"metrics:{user_id}:{date}"
    cached = redis.get(redis_key)
    if cached:
        return json.loads(cached)
    
    # Level 3: Database
    metric = db.query(DailyMetric).filter_by(
        user_id=user_id, date=date
    ).first()
    
    # Populate caches
    redis.setex(redis_key, 3600, json.dumps(metric.to_dict()))
    LOCAL_CACHE[user_id] = metric
    
    return metric
```

---

## Version History

### v1.0.0 (Current)
- Initial release
- 11 data models
- 20+ API endpoints
- Churn prediction
- Dashboard support
- Report generation
- Cohort analysis

---

## Support & Contribution

For issues, questions, or contributions, please contact the platform team or submit issues to the team repository.

**Last Updated**: January 2024
**Status**: Production Ready