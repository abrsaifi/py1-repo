# File Converter SaaS - Quick Start Guide

Get the application running in 5 minutes!

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js 14+ (for frontend)

## Quick Setup (Development)

### 1. Environment Setup
\\\ash
# Clone repository
git clone <repository-url>
cd file-converter-saas

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
\\\

### 2. Database Init
\\\ash
# Run migrations
python scripts/run_migrations.py

# Seed data
python database/seed/seeds.py
\\\

### 3. Start Services (Terminal Tabs)

**Tab 1 - API Gateway**:
\\\ash
python -m services.api_gateway.main
\\\

**Tab 2 - Conversion Service**:
\\\ash
python -m services.conversion_service.main
\\\

**Tab 3 - Worker**:
\\\ash
python -m workers.conversion_workers.pdf_worker
\\\

**Tab 4 - Frontend**:
\\\ash
cd apps/web
npm install
npm start
\\\

## Docker Setup (Recommended)

\\\ash
docker-compose -f infra/docker-compose.dev.yml up
\\\

## Project Structure

See ARCHITECTURE.md for complete structure overview.

## Next Steps

- Read ARCHITECTURE.md
- Check SERVICE_ARCHITECTURE.md
- Review MIGRATION_GUIDE.md

---

**Architecture Version**: 1.0.0 (Enterprise SaaS)  
**Last Updated**: March 2026
