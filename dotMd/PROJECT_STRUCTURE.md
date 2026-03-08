# Project Structure Overview

This document visualizes the complete new project structure.

## Complete Directory Tree

```
file-converter-saas/
│
├── 📱 apps/                                    # Client Applications
│   ├── web/                                    # Web + PWA Frontend
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── converter/                  # Converter UI
│   │   │   │   ├── dashboard/                  # User dashboard
│   │   │   │   ├── profile/                    # User profile
│   │   │   │   ├── billing/                    # Billing page
│   │   │   │   ├── admin/                      # Admin panel
│   │   │   │   └── ui/                         # Shared UI components
│   │   │   ├── pages/
│   │   │   │   ├── home/                       # Landing page
│   │   │   │   ├── convert/                    # Conversion page
│   │   │   │   ├── dashboard/                  # Dashboard page
│   │   │   │   ├── pricing/                    # Pricing page
│   │   │   │   ├── login/                      # Login page
│   │   │   │   ├── register/                   # Register page
│   │   │   │   └── admin/                      # Admin page
│   │   │   ├── hooks/                          # React hooks
│   │   │   ├── context/                        # Context providers
│   │   │   ├── services/                       # API clients
│   │   │   ├── pwa/                            # PWA manifest
│   │   │   │   ├── manifest.json
│   │   │   │   └── service-worker.js
│   │   │   ├── static/                         # Static assets
│   │   │   └── templates/                      # HTML templates
│   │   └── package.json
│   │
│   └── admin-panel/                            # Optional separate admin UI
│       ├── src/
│       └── package.json
│
├── 🔧 services/                                # Microservices
│   │
│   ├── api-gateway/                            # API Gateway (Main Entry Point)
│   │   ├── main.py                             # Entry point
│   │   ├── config.py                           # Configuration
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── conversion.py
│   │   │   ├── user.py
│   │   │   └── admin.py
│   │   ├── middlewares/
│   │   │   ├── auth.py                         # JWT validation
│   │   │   ├── rate_limiter.py                 # Rate limiting
│   │   │   └── logging.py                      # Request logging
│   │   └── requirements.txt
│   │
│   ├── auth-service/                           # Authentication Service
│   │   ├── main.py
│   │   ├── models/
│   │   │   └── user.py
│   │   ├── routes/
│   │   │   ├── register.py
│   │   │   ├── login.py
│   │   │   └── token.py
│   │   ├── security/
│   │   │   ├── jwt.py
│   │   │   └── password.py
│   │   └── requirements.txt
│   │
│   ├── user-service/                           # User Data Service
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── profile.py
│   │   │   ├── history.py
│   │   │   ├── usage.py
│   │   │   └── subscription.py
│   │   └── requirements.txt
│   │
│   ├── conversion-service/                     # Conversion Job Management
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── create_job.py
│   │   │   ├── job_status.py
│   │   │   ├── document_conversion.py
│   │   │   ├── image_processing.py
│   │   │   ├── pdf_tools.py
│   │   │   ├── preview.py
│   │   │   ├── watermark.py
│   │   │   ├── ocr.py
│   │   │   └── websocket.py
│   │   ├── queue/
│   │   │   ├── enqueue.py                      # Job queuing
│   │   │   └── status.py                       # Status checking
│   │   ├── validators/
│   │   │   └── file_validator.py               # File validation
│   │   └── requirements.txt
│   │
│   ├── billing-service/                        # Billing & Subscriptions
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── subscription.py
│   │   │   ├── payment.py
│   │   │   └── invoice.py
│   │   └── requirements.txt
│   │
│   └── analytics-service/                      # Analytics & Metrics
│       ├── main.py
│       ├── routes/
│       │   ├── metrics.py
│       │   └── reports.py
│       └── requirements.txt
│
├── 🚀 workers/                                 # Background Workers
│   │
│   ├── conversion-workers/                     # CPU-Intensive Conversions
│   │   ├── __init__.py
│   │   ├── pdf_worker.py                       # PDF conversions
│   │   ├── image_worker.py                     # Image conversions
│   │   ├── doc_worker.py                       # Document conversions
│   │   ├── compress_worker.py                  # Compression
│   │   └── requirements.txt
│   │
│   ├── cleanup-worker/                         # File Retention
│   │   ├── __init__.py
│   │   ├── delete_expired_files.py
│   │   └── requirements.txt
│   │
│   └── priority-worker/                        # Premium Queue
│       ├── __init__.py
│       ├── priority_queue.py
│       └── requirements.txt
│
├── 📦 packages/                                # Shared Code
│   │
│   ├── shared-models/                          # Data Models
│   │   ├── __init__.py
│   │   ├── models.py                           # User, Job, Subscription models
│   │   └── requirements.txt
│   │
│   ├── shared-utils/                           # Common Utilities
│   │   ├── __init__.py
│   │   ├── utils.py                            # FileValidator, PasswordHelper, etc.
│   │   └── requirements.txt
│   │
│   └── shared-config/                          # Centralized Config
│       ├── __init__.py
│       ├── config.py                           # DevelopmentConfig, ProductionConfig
│       └── requirements.txt
│
├── 🏗 infra/                                   # Infrastructure
│   │
│   ├── docker/                                 # Docker Configuration
│   │   ├── Dockerfile                          # Service container
│   │   ├── Dockerfile.api-gateway
│   │   ├── Dockerfile.worker
│   │   └── .dockerignore
│   │
│   ├── docker-compose.dev.yml                  # Development orchestration
│   ├── docker-compose.prod.yml                 # Production orchestration
│   ├── docker-compose.yml                      # Base config
│   │
│   ├── nginx/                                  # Reverse Proxy
│   │   ├── nginx.conf                          # Main config
│   │   └── ssl/                                # SSL certificates
│   │
│   ├── k8s/                                    # Kubernetes (Future)
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── README.md
│   │
│   └── terraform/                              # Infrastructure as Code (Future)
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
├── 💾 database/                                # Database
│   │
│   ├── migrations/                             # Schema Migrations
│   │   ├── 20260301_120000_init_schema.py
│   │   ├── 20260302_130000_add_auth_tokens.py
│   │   └── README.md
│   │
│   └── seed/                                   # Test Data
│       ├── seeds.py
│       └── fixtures/
│
├── 📊 monitoring/                              # Observability
│   │
│   ├── prometheus/                             # Metrics Collection
│   │   ├── prometheus.yml                      # Scrape config
│   │   └── alerts.yaml                         # Alert rules
│   │
│   └── grafana/                                # Dashboards
│       ├── dashboards/
│       │   ├── services.json
│       │   ├── workers.json
│       │   └── users.json
│       └── provisioning/
│
├── 🛠 scripts/                                 # Utility Scripts
│   ├── run_migrations.py
│   ├── seed_database.py
│   ├── start_services.sh
│   ├── deploy.sh
│   └── backup.sh
│
├── 📚 tests/                                   # Test Suite
│   ├── conftest.py
│   ├── test_all_features.py
│   ├── integration_test.py
│   └── ...
│
├── 📖 Documentation
│   ├── README.md                               # Main readme
│   ├── ARCHITECTURE.md                         # Architecture overview
│   ├── SERVICE_ARCHITECTURE.md                 # Service details
│   ├── MIGRATION_GUIDE.md                      # Legacy migration
│   ├── QUICKSTART.md                           # Quick start guide
│   ├── USER_GUIDE.md                           # User documentation
│   ├── DEPLOYMENT.md                           # Deployment guide
│   ├── API_REFERENCE.md                        # API documentation
│   └── docs/
│       ├── adr/                                # Architecture Decision Records
│       ├── api/                                # API documentation
│       └── guides/
│
├── Configuration Files
│   ├── .env.example                            # Example environment variables
│   ├── .env.production.template                # Production template
│   ├── .gitignore                              # Git ignore rules
│   ├── .github/
│   │   └── workflows/                          # CI/CD workflows
│   ├── pyproject.toml                          # Python project config
│   ├── requirements.txt                        # Python dependencies
│   └── requirements-dev.txt                    # Development dependencies
│
└── Version Control & Root Files
    ├── .git/                                   # Git repository
    ├── .gitignore
    ├── LICENSE
    └── README.md

```

## File Count Summary

```
Total Files: ~500+
├── Python Files: ~150
├── Configuration Files: ~30
├── Frontend Files: ~100
├── Tests: ~80
├── Documentation: ~40
└── Infrastructure: ~100
```

## Key Directories Explained

### `apps/`
Client-facing applications. Currently web + PWA, extensible for mobile.

### `services/`
Independent microservices, each with its own:
- Routes/handlers
- Database models (logical ownership)
- Tests
- Requirements

### `workers/`
Background job processors. Scale independently based on load.

### `packages/`
Shared code to avoid duplication:
- Models shared across all services
- Utilities (validators, helpers)
- Configuration management

### `infra/`
Everything needed to run the application:
- Docker containers
- Orchestration (docker-compose)
- Kubernetes configs (future)
- Monitoring setup

### `database/`
Database lifecycle management:
- Schema migrations (version control for DB)
- Seed data for testing

### `monitoring/`
Observability stack configuration:
- Metrics collection
- Dashboards
- Alerting

## Database Tables

```
┌─────────────────────────────────────────┐
│          Shared PostgreSQL              │
├─────────────────────────────────────────┤
│ users                                   │
│ auth_tokens                             │
│ conversion_jobs                         │
│ file_metadata                           │
│ subscriptions                           │
│ usage_logs                              │
│ system_metrics                          │
│ invoices                                │
│ api_keys                                │
└─────────────────────────────────────────┘
```

## Service Ports

```
API Gateway:         5000
Auth Service:        5001
User Service:        5002
Conversion Service:  5003
Billing Service:     5004
Analytics Service:   5005

PostgreSQL:          5432
Redis:               6379
Prometheus:          9090
Grafana:             3000
Frontend:            3000
```

## How to Navigate

1. **Starting out?** → Read `ARCHITECTURE.md`
2. **Quick setup?** → Follow `QUICKSTART.md`
3. **Migrating code?** → See `MIGRATION_GUIDE.md`
4. **Deploying?** → Check `DEPLOYMENT.md`
5. **API details?** → Review `API_REFERENCE.md`
6. **Service specifics?** → Each service has its own `README.md`

---

**This structure supports scaling from 100 to 100 million users.**
