# File Converter SaaS - Enterprise Architecture

This is the structured README for the completely redesigned file converter application using a scalable SaaS infrastructure architecture.

## 🏗 Architecture Overview

The project is organized as a **monorepo** with clear separation of concerns:

```
file-converter-saas/
├── apps/                      # Client applications
│   ├── web/                   # Desktop + PWA frontend
│   └── admin-panel/           # Admin dashboard
│
├── services/                  # Microservices
│   ├── api-gateway/           # API entry point
│   ├── auth-service/          # Authentication
│   ├── user-service/          # User dashboard
│   ├── conversion-service/    # Job management
│   ├── billing-service/       # Payments
│   └── analytics-service/     # Metrics & tracking
│
├── workers/                   # Background workers
│   ├── conversion-workers/    # CPU-intensive conversions
│   ├── cleanup-worker/        # File retention
│   └── priority-worker/       # Premium user queue
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
- Workers scale independently based on load
- Each service can have different resource requirements
- Horizontal scaling with load balancing

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

## 📦 Services Breakdown

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
Four specialized workers handle different file types:

- **PDF Worker** - Document to PDF conversions
- **Image Worker** - Image format conversions
- **Document Worker** - Office document conversions (DOCX, XLSX, PPTX)
- **Compression Worker** - File compression and archiving

### Cleanup Worker (`workers/cleanup-worker/`)
- Automatic file deletion based on retention policy
- Orphaned file detection
- Storage optimization

### Priority Worker (`workers/priority-worker/`)
- Handles premium user jobs with SLA guarantees
- Tier-based queue management
- Performance monitoring

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
