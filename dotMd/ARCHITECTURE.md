# File Converter SaaS - Enterprise Architecture

This document is a reference architecture for the broader SaaS decomposition work in the repository.
The current production-oriented runtime in this workspace remains the modular Flask application under `app/`, with background processing through `app/celery_config.py` and `app/tasks.py`.

## 🏗 Architecture Overview

The repository contains a mix of active runtime code and historical/target monorepo structure artifacts:

```
file-converter-saas/
├── apps/                      # Client applications
│   ├── web/                   # Desktop + PWA frontend
│   └── admin-panel/           # Admin dashboard
│
├── services/                  # Historical/target service split artifacts
│   ├── api-gateway/           # API entry point
│   ├── auth-service/          # Authentication
│   ├── user-service/          # User dashboard
│   ├── conversion-service/    # Job management
│   ├── billing-service/       # Payments
│   └── analytics-service/     # Metrics & tracking
│
├── workers/                   # Compatibility launchers for Celery queues
│   ├── conversion-workers/    # Launchers/adapters for the conversions queue
│   ├── cleanup-worker/        # Launcher/adapter for the maintenance queue
│   └── priority-worker/       # Launcher/adapter for the critical queue
│
├── packages/                  # Shared code
│   ├── shared-models/         # Data structures
│   ├── shared-utils/          # Common utilities
│   └── shared-config/         # Configuration
│
├── infra/                     # Infrastructure
│   ├── docker/                # Docker configs
│   ├── nginx/                 # Reverse proxy
│   ├── k8s/                   # Kubernetes (future)
│   └── terraform/             # IaC (future)
│
├── database/                  # Database
│   ├── migrations/            # Schema versions
│   └── seed/                  # Initial data
│
├── monitoring/                # Observability
│   ├── prometheus/            # Metrics
│   └── grafana/              # Dashboards
│
└── scripts/                   # Utilities
```

## 🎯 Key Benefits of This Architecture

### 1. **Scalability**
- Celery workers scale independently based on load
- The modular Flask package can be extended behind load balancing
- Historical service split docs remain useful for future decomposition

### 2. **Reliability**
- Service isolation prevents cascading failures
- Retry mechanisms and dead-letter queues
- Health checks and monitoring per service

### 3. **Development Velocity**
- Teams can work independently on services
- Clear API contracts between services
- Easier testing and debugging

### 4. **Maintainability**
- Single responsibility per service
- Shared utilities reduce code duplication
- Centralized configuration management

## 📦 Reference Service Breakdown

These sections describe the intended service decomposition, not the current single-runtime deployment shape.

### API Gateway (`services/api-gateway/`)
- Central entry point for all requests
- JWT validation & authentication
- Rate limiting
- Request logging

### Auth Service (`services/auth-service/`)
- User registration and login
- JWT token generation
- Password hashing (PBKDF2)
- Role management (user, admin)

### User Service (`services/user-service/`)
- User profiles and settings
- Conversion history
- Usage analytics
- Subscription management

### Conversion Service (`services/conversion-service/`)
- Job creation and validation
- File upload handling
- Queue management
- Job tracking

### Billing Service (`services/billing-service/`)
- Subscription management
- Payment processing integration
- Usage tracking & quotas
- Invoice generation

### Analytics Service (`services/analytics-service/`)
- Usage metrics collection
- Performance monitoring
- User behavior tracking
- Reporting endpoints

## 🔧 Workers

### Conversion Workers (`workers/conversion-workers/`)
The `workers/` tree is kept as a compatibility layer for older scripts and deployment notes.
The live background-processing path is the package Celery app in `app/celery_config.py` with tasks in `app/tasks.py`.
The compatibility launchers map to the shared Celery queues instead of implementing a separate worker system.

- **PDF Worker** - launches the `conversions` queue and dispatches `app.tasks.process_pdf`
- **Image Worker** - launches the `conversions` queue and dispatches `app.tasks.process_image`
- **Document Worker** - launches the `conversions` queue and dispatches `app.tasks.convert_file`
- **Compression Worker** - launches the `maintenance` queue and dispatches `app.tasks.long_running_operation`

### Cleanup Worker (`workers/cleanup-worker/`)
- Compatibility launcher for maintenance cleanup tasks
- Queues `app.tasks.cleanup_old_uploads`
- Uses the shared `maintenance` Celery queue

### Priority Worker (`workers/priority-worker/`)
- Compatibility launcher for premium routing
- Sends premium jobs to the shared `critical` Celery queue
- Keeps older worker entrypoints usable without maintaining a second async stack

## 📊 Shared Packages

### `packages/shared-models/`
Data models used across all services:
- User, ConversionJob, Subscription
- FileFormat, ConversionStatus enums
- UsageLog, SystemMetrics

### `packages/shared-utils/`
Common utilities:
- FileValidator - File type and size validation
- PasswordHelper - Secure password hashing
- TokenHelper - Token generation
- DateTimeHelper - Timestamp management
- JSONHelper - JSON serialization
- Logger - Centralized logging

### `packages/shared-config/`
Configuration management:
- DevelopmentConfig
- ProductionConfig
- TestingConfig
- Environment-based config loading

## 🌐 Frontend (`apps/web/`)

Single-codebase frontend supporting:
- **Desktop Web** - Responsive web interface
- **PWA** - Progressive Web App (installable)
- **Components**: Converter, Dashboard, Profile, Billing, Admin
- **Pages**: Home, Convert, Dashboard, Pricing, Login, Register, Admin

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js 14+ (for frontend)

### Installation

```bash
# Clone and setup
git clone <repo>
cd file-converter-saas

# Backend setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Frontend setup
cd apps/web
npm install

# Run services (development)
python -m services.api_gateway.main
python -m services.auth_service.main
python -m services.conversion_service.main
python -m workers.conversion_workers.pdf_worker
# ... etc
```

### Docker Deployment

```bash
# Development
docker-compose -f infra/docker-compose.dev.yml up

# Production
docker-compose -f infra/docker-compose.prod.yml up
```

## 📚 Documentation Structure

- **Service Docs**: Each service has its own README
- **API Docs**: OpenAPI/Swagger specs in each service
- **Deployment**: See `infra/` directory
- **Architecture Decisions**: ADRs in `docs/adr/`

## 🔄 Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes** in specific service(s)

3. **Test**
   ```bash
   pytest services/my-service/tests/
   ```

4. **Create Pull Request** with clear description

5. **Code Review** by team

6. **Merge & Deploy** (CI/CD pipeline)

## 🔒 Security Features

- **JWT Authentication** with expiry
- **PBKDF2 Password Hashing**
- **Rate Limiting** per IP
- **File Validation** (type & size)
- **CORS Configuration**
- **Secrets Management** via environment variables

## 📈 Monitoring & Observability

- **Prometheus** metrics collection
- **Grafana** dashboards
- **Centralized Logging**
- **Health Check Endpoints** per service
- **APM Integration Ready**

## 🚀 Future Roadmap

- [ ] Kubernetes deployment configs
- [ ] Multi-region support
- [ ] Advanced analytics
- [ ] Mobile app (React Native)
- [ ] Payment processor integration (Stripe)
- [ ] WebSocket real-time updates
- [ ] GraphQL API option

## 📞 Support

For issues or questions about architecture:
1. Check service-specific README files
2. Review API documentation
3. Check Slack channel or GitHub issues

## 📄 License

MIT License - see LICENSE file for details

---

**Last Updated**: March 2026  
**Architecture Version**: 1.0.0 (Full Enterprise SaaS)
