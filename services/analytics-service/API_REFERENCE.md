"""
Phase 10 Analytics Service - Complete API Reference
Comprehensive documentation for all 101+ endpoints, models, and configurations
"""

# ============================================================================
# PHASE 10 ANALYTICS SERVICE - COMPLETE API REFERENCE
# ============================================================================

## Overview

The Phase 10 Analytics Service is a comprehensive microservice for collecting, 
processing, and querying analytics data. It provides 101+ RESTful endpoints 
organized across 7 blueprint modules with support for multi-tenancy, 
authentication, and complex metric aggregations.

**Service Details:**
- Port: 5009
- Framework: Flask 2.3.0
- Database: PostgreSQL with SQLAlchemy ORM
- Cache: Redis for query results and dashboards
- Authentication: JWT (1-hour access tokens, 30-day refresh)
- Multi-tenancy: Required tenant header on all requests


---

## Table of Contents

1. [Authentication & Authorization](#authentication)
2. [Metrics Endpoints (15 endpoints)](#metrics-endpoints)
3. [Dashboards Endpoints (17 endpoints)](#dashboards-endpoints)
4. [Reports Endpoints (15 endpoints)](#reports-endpoints)
5. [Alerts Endpoints (18 endpoints)](#alerts-endpoints)
6. [Custom Metrics Endpoints (8 endpoints)](#custom-metrics-endpoints)
7. [Queries Endpoints (13 endpoints)](#queries-endpoints)
8. [Export Endpoints (15 endpoints)](#export-endpoints)
9. [Data Models](#data-models)
10. [Configuration](#configuration)
11. [Error Handling](#error-handling)
12. [Rate Limiting](#rate-limiting)
13. [Deployment Guide](#deployment)
14. [Troubleshooting](#troubleshooting)


---

## Authentication & Authorization {#authentication}

### Request Headers

All requests (except health checks) require the following headers:

```
Authorization: Bearer <JWT_TOKEN>
X-Tenant-ID: <TENANT_ID>
X-Request-ID: <UUID>
Content-Type: application/json
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "tenant_id": "tenant-001",
    "user_id": "user-123",
    "iat": 1677123456,
    "exp": 1677127056
  }
}
```

### Token Expiration

- **Access Token**: 1 hour
- **Refresh Token**: 30 days
- **Algorithm**: HS256 (HMAC SHA-256)

### Response Status Codes

- `200 OK` - Successful GET request
- `201 Created` - Successful POST request  
- `202 Accepted` - Async operation accepted
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Missing/invalid auth
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error


---

## Metrics Endpoints (15+) {#metrics-endpoints}

### 1. Get System Metrics
```
GET /api/metrics/system
```

**Parameters:**
- `service_name` (optional): Filter by service
- `metric_name` (optional): Filter by metric name
- `aggregation_level` (optional): minute, hour, day, week, month, year
- `start_time` (optional): ISO 8601 timestamp
- `end_time` (optional): ISO 8601 timestamp
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Results per page (default: 50, max: 500)

**Response (200 OK):**
```json
{
  "count": 150,
  "metrics": [
    {
      "id": "metric-uuid",
      "tenant_id": "tenant-001",
      "service_name": "auth-service",
      "metric_name": "cpu_usage",
      "aggregation_level": "hour",
      "value": 45.2,
      "min_value": 40.0,
      "max_value": 50.0,
      "timestamp": "2024-03-04T10:00:00Z",
      "period_start": "2024-03-04T09:00:00Z",
      "period_end": "2024-03-04T10:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 50
}
```


### 2. Get Service Metrics
```
GET /api/metrics/service
```

**Parameters:**
- `service_name` (optional): Filter by service name
- `start_time` (optional): ISO 8601 timestamp
- `end_time` (optional): ISO 8601 timestamp

**Response (200 OK):**
```json
{
  "count": 50,
  "metrics": [
    {
      "id": "metric-uuid",
      "service_name": "user-service",
      "period_start": "2024-03-04T09:00:00Z",
      "period_end": "2024-03-04T10:00:00Z",
      "response_time_p50": 100.5,
      "response_time_p95": 250.3,
      "response_time_p99": 500.1,
      "response_time_avg": 150.2,
      "total_requests": 10000,
      "successful_requests": 9980,
      "failed_requests": 20,
      "error_rate": 0.2,
      "http_4xx_count": 15,
      "http_5xx_count": 5,
      "uptime_percent": 99.95,
      "cpu_percent": 45.2,
      "memory_percent": 62.5,
      "disk_percent": 78.3
    }
  ]
}
```


### 3. Get User Activity Metrics
```
GET /api/metrics/activity
```

**Response (200 OK):**
```json
{
  "metrics": [
    {
      "id": "activity-uuid",
      "period_start": "2024-03-04T00:00:00Z",
      "period_end": "2024-03-05T00:00:00Z",
      "total_users": 5000,
      "active_users": 2500,
      "dau": 2500,
      "wau": 4200,
      "mau": 4800,
      "dau_wau_ratio": 59.5,
      "dau_mau_ratio": 52.1,
      "new_users": 150,
      "returned_users": 2000,
      "churned_users": 100,
      "total_sessions": 15000,
      "avg_session_duration": 300.5,
      "bounce_rate": 25.3
    }
  ]
}
```


### 4. Get Business Metrics
```
GET /api/metrics/business
```

**Response (200 OK):**
```json
{
  "metrics": [
    {
      "id": "business-uuid",
      "period_start": "2024-03-01T00:00:00Z",
      "period_end": "2024-03-04T00:00:00Z",
      "mrr": 50000.00,
      "arr": 600000.00,
      "revenue": 150250.75,
      "total_customers": 250,
      "new_customers": 20,
      "churned_customers": 3,
      "churn_rate": 1.2,
      "retention_rate": 98.8,
      "ltv": 10000.00,
      "cac": 500.00,
      "ltv_cac_ratio": 20.0,
      "nrr": 110.5,
      "mom_growth": 5.2,
      "yoy_growth": 45.3
    }
  ]
}
```


### 5-15. Additional Metric Endpoints

- `GET /api/metrics/{id}` - Get single metric by ID
- `GET /api/metrics/aggregate` - Get aggregated metrics
- `GET /api/metrics/health` - Service health metrics
- `POST /api/metrics/calculate` - Calculate derived metrics
- `GET /api/metrics/forecast` - Forecast metrics (AI-assisted)
- `GET /api/metrics/anomalies` - Detect anomalies
- `GET /api/metrics/correlations` - Find metric correlations
- `GET /api/metrics/compare` - Compare metrics across services
- `GET /api/metrics/summary` - Summary statistics
- `POST /api/metrics/bulk` - Bulk metric ingestion
- `GET /api/metrics/export` - Export metrics to CSV


---

## Dashboards Endpoints (17) {#dashboards-endpoints}

### 1. List Dashboards
```
GET /api/dashboards
```

**Parameters:**
- `dashboard_type` (optional): executive, operational, technical, custom
- `page` (optional): Page number
- `per_page` (optional): Results per page

**Response (200 OK):**
```json
{
  "count": 10,
  "dashboards": [
    {
      "id": "dashboard-uuid",
      "tenant_id": "tenant-001",
      "name": "Executive Dashboard",
      "description": "High-level business metrics",
      "dashboard_type": "executive",
      "owner_user_id": "user-123",
      "is_public": false,
      "view_count": 150,
      "widget_count": 8,
      "created_at": "2024-02-01T10:00:00Z",
      "updated_at": "2024-03-04T15:30:00Z"
    }
  ]
}
```


### 2. Create Dashboard
```
POST /api/dashboards
```

**Request Body:**
```json
{
  "name": "New Dashboard",
  "description": "Dashboard description",
  "dashboard_type": "custom",
  "is_public": false,
  "refresh_interval": 300
}
```

**Response (201 Created):**
```json
{
  "id": "dashboard-new-uuid",
  "name": "New Dashboard",
  "dashboard_type": "custom",
  "status": "active"
}
```


### 3. Get Dashboard
```
GET /api/dashboards/{dashboard_id}
```

**Response (200 OK):**
```json
{
  "id": "dashboard-uuid",
  "name": "Executive Dashboard",
  "dashboard_type": "executive",
  "widgets": [
    {
      "id": "widget-1",
      "type": "metric",
      "title": "Revenue",
      "metric": "mrr",
      "position": {"x": 0, "y": 0, "w": 4, "h": 3}
    },
    {
      "id": "widget-2",
      "type": "chart",
      "title": "Growth Trend",
      "metric": "growth_rate",
      "position": {"x": 4, "y": 0, "w": 8, "h": 4}
    }
  ],
  "layout": "grid",
  "refresh_interval": 300
}
```


### 4. Update Dashboard
```
PUT /api/dashboards/{dashboard_id}
```

**Request Body:**
```json
{
  "name": "Updated Dashboard",
  "description": "Updated description",
  "refresh_interval": 600
}
```


### 5. Delete Dashboard
```
DELETE /api/dashboards/{dashboard_id}
```

**Response (204 No Content)**


### 6. Get Dashboard Widgets
```
GET /api/dashboards/{dashboard_id}/widgets
```

**Response (200 OK):**
```json
{
  "widgets": [
    {
      "id": "widget-1",
      "type": "metric",
      "title": "Revenue",
      "metric": "mrr",
      "config": {"format": "currency"}
    }
  ]
}
```


### 7. Add Widget
```
POST /api/dashboards/{dashboard_id}/widgets
```

**Request Body:**
```json
{
  "type": "metric",
  "title": "New Widget",
  "metric": "response_time_p95",
  "position": {"x": 0, "y": 0, "w": 4, "h": 3}
}
```


### 8. Update Widget
```
PUT /api/dashboards/{dashboard_id}/widgets/{widget_id}
```

**Request Body:**
```json
{
  "title": "Updated Widget",
  "position": {"x": 4, "y": 0, "w": 4, "h": 3}
}
```


### 9. Delete Widget
```
DELETE /api/dashboards/{dashboard_id}/widgets/{widget_id}
```


### 10. Share Dashboard
```
POST /api/dashboards/{dashboard_id}/share
```

**Request Body:**
```json
{
  "user_ids": ["user-2", "user-3"],
  "group_ids": ["group-1"],
  "permission_level": "view"
}
```


### 11. Pin Dashboard
```
POST /api/dashboards/{dashboard_id}/pin
```

**Response (200 OK):**
```json
{"pinned": true, "position": 1}
```


### 12. Unpin Dashboard
```
POST /api/dashboards/{dashboard_id}/unpin
```


### 13. Refresh Dashboard
```
POST /api/dashboards/{dashboard_id}/refresh
```

**Response (200 OK):**
```json
{"refreshed": true, "timestamp": "2024-03-04T15:35:00Z"}
```


### 14. Get Dashboard Templates
```
GET /api/dashboards/templates
```

**Response (200 OK):**
```json
{
  "templates": [
    {
      "id": "template-1",
      "name": "Executive Summary",
      "description": "High-level metrics",
      "preview_url": "/templates/executive-preview.png"
    }
  ]
}
```


### 15-17. Additional Dashboard Endpoints

- `GET /api/dashboards/{id}/sharing` - Get sharing settings
- `POST /api/dashboards/{id}/duplicate` - Duplicate dashboard
- `GET /api/dashboards/trending` - Get trending dashboards


---

## Reports Endpoints (15) {#reports-endpoints}

### 1. List Reports
```
GET /api/reports
```

**Parameters:**
- `report_type` (optional): summary, detailed, executive
- `status` (optional): draft, scheduled, generated, archived
- `page` (optional): Page number
- `per_page` (optional): Results per page

**Response (200 OK):**
```json
{
  "count": 25,
  "reports": [
    {
      "id": "report-uuid",
      "name": "Monthly Performance Report",
      "report_type": "summary",
      "status": "scheduled",
      "schedule": "monthly",
      "last_generated": "2024-03-01T00:00:00Z",
      "next_generation": "2024-04-01T00:00:00Z",
      "created_at": "2024-02-01T10:00:00Z"
    }
  ]
}
```


### 2. Create Report
```
POST /api/reports
```

**Request Body:**
```json
{
  "name": "Custom Report",
  "report_type": "detailed",
  "description": "Custom analytics report",
  "metrics": ["mrr", "growth_rate", "churn_rate"],
  "segments": [
    {"name": "by_region", "field": "region"},
    {"name": "by_product", "field": "product"}
  ]
}
```


### 3. Get Report
```
GET /api/reports/{report_id}
```

**Response (200 OK):**
```json
{
  "id": "report-uuid",
  "name": "Monthly Performance Report",
  "report_type": "summary",
  "metrics": ["mrr", "growth_rate"],
  "segments": [],
  "filter_sets": [
    {"name": "active_customers", "filters": {"status": "active"}}
  ],
  "recipients": ["admin@example.com"],
  "schedule": "monthly"
}
```


### 4. Update Report
```
PUT /api/reports/{report_id}
```

**Request Body:**
```json
{
  "name": "Updated Report",
  "schedule": "weekly",
  "recipients": ["admin@example.com", "manager@example.com"]
}
```


### 5. Delete Report
```
DELETE /api/reports/{report_id}
```


### 6. Generate Report
```
POST /api/reports/{report_id}/generate
```

**Parameters:**
- `async` (optional): true - Generate asynchronously (default: true)

**Response (202 Accepted):**
```json
{
  "report_id": "report-uuid",
  "generation_id": "gen-uuid",
  "status": "pending",
  "estimated_duration": 30
}
```


### 7. Get Generation Status
```
GET /api/reports/{report_id}/generations/{generation_id}
```

**Response (200 OK):**
```json
{
  "generation_id": "gen-uuid",
  "status": "completed",
  "progress": 100,
  "generated_at": "2024-03-04T15:35:00Z",
  "file_url": "/reports/report-uuid/gen-uuid/report.pdf",
  "file_size": 2048000
}
```


### 8. Download Report
```
GET /api/reports/{report_id}/download/{generation_id}
```

**Query Parameters:**
- `format` (optional): pdf (default), xlsx, html, csv

**Response (200 OK):**
```
[File content - Binary PDF/XLSX data]
```


### 9. Schedule Report
```
POST /api/reports/{report_id}/schedule
```

**Request Body:**
```json
{
  "frequency": "weekly",
  "day_of_week": "monday",
  "time": "09:00",
  "timezone": "UTC",
  "recipients": ["admin@example.com"],
  "format": "pdf"
}
```


### 10. Get Report History
```
GET /api/reports/{report_id}/history
```

**Response (200 OK):**
```json
{
  "generations": [
    {
      "generation_id": "gen-uuid-1",
      "generated_at": "2024-03-04T15:35:00Z",
      "status": "completed",
      "file_url": "/reports/report-uuid/gen-uuid-1/report.pdf"
    }
  ]
}
```


### 11. Get Report Templates
```
GET /api/reports/templates
```

**Response (200 OK):**
```json
{
  "templates": [
    {
      "id": "template-1",
      "name": "Executive Summary",
      "description": "High-level metrics",
      "metrics": ["mrr", "growth_rate"],
      "format": ["pdf", "xlsx"]
    }
  ]
}
```


### 12. Share Report
```
POST /api/reports/{report_id}/share
```

**Request Body:**
```json
{
  "user_ids": ["user-2", "user-3"],
  "permission": "view"
}
```


### 13. Archive Report
```
POST /api/reports/{report_id}/archive
```


### 14. Unarchive Report
```
POST /api/reports/{report_id}/unarchive
```


### 15. Export Report Config
```
POST /api/reports/{report_id}/export-config
```

**Response (200 OK):**
```json
{
  "format": "json",
  "config": {
    "name": "Monthly Report",
    "metrics": ["mrr"],
    "schedule": "monthly"
  }
}
```


---

## Alerts Endpoints (18) {#alerts-endpoints}

### 1. List Alerts
```
GET /api/alerts
```

**Parameters:**
- `status` (optional): active, acknowledged, resolved
- `severity` (optional): info, warning, critical, emergency
- `metric_name` (optional): Filter by metric
- `page` (optional): Page number

**Response (200 OK):**
```json
{
  "count": 45,
  "alerts": [
    {
      "id": "alert-uuid",
      "metric_name": "error_rate",
      "condition_type": "threshold",
      "threshold_value": 5.0,
      "comparison_operator": ">",
      "severity": "critical",
      "is_active": true,
      "evaluation_frequency": "5m",
      "created_at": "2024-02-01T10:00:00Z",
      "last_evaluated": "2024-03-04T15:30:00Z"
    }
  ]
}
```


### 2. Create Alert
```
POST /api/alerts
```

**Request Body:**
```json
{
  "metric_name": "error_rate",
  "condition_type": "threshold",
  "threshold_value": 5.0,
  "comparison_operator": ">",
  "severity": "critical",
  "evaluation_frequency": "5m",
  "notification_channels": ["email", "slack"],
  "recipients": ["admin@example.com"],
  "slack_webhook": "https://hooks.slack.com/..."
}
```


### 3. Get Alert
```
GET /api/alerts/{alert_id}
```

**Response (200 OK):** [Full alert details]


### 4. Update Alert
```
PUT /api/alerts/{alert_id}
```

**Request Body:**
```json
{
  "threshold_value": 10.0,
  "severity": "warning",
  "is_active": true
}
```


### 5. Delete Alert
```
DELETE /api/alerts/{alert_id}
```


### 6. Get Alert Events
```
GET /api/alerts/{alert_id}/events
```

**Parameters:**
- `status` (optional): active, acknowledged, resolved
- `limit` (optional): Results limit (default: 100)

**Response (200 OK):**
```json
{
  "events": [
    {
      "event_id": "event-uuid",
      "alert_id": "alert-uuid",
      "triggered_at": "2024-03-04T15:30:00Z",
      "metric_value": 7.5,
      "threshold_value": 5.0,
      "severity": "critical",
      "status": "active",
      "acknowledged_at": null,
      "acknowledged_by": null
    }
  ]
}
```


### 7. Acknowledge Alert Event
```
POST /api/alerts/{alert_id}/events/{event_id}/acknowledge
```

**Request Body:**
```json
{
  "notes": "Investigating issue"
}
```

**Response (200 OK):**
```json
{
  "event_id": "event-uuid",
  "status": "acknowledged",
  "acknowledged_at": "2024-03-04T15:35:00Z"
}
```


### 8. Resolve Alert Event
```
POST /api/alerts/{alert_id}/events/{event_id}/resolve
```

**Request Body:**
```json
{
  "resolution": "Issue resolved"
}
```


### 9. Get Alert Rules
```
GET /api/alerts/rules
```

**Response (200 OK):**
```json
{
  "rules": [
    {
      "id": "rule-1",
      "name": "High Error Rate",
      "condition": "error_rate > 5.0",
      "severity": "critical",
      "enabled": true
    }
  ]
}
```


### 10. Create Alert Rule
```
POST /api/alerts/rules
```

**Request Body:**
```json
{
  "name": "Custom Rule",
  "condition": "response_time_p99 > 500",
  "severity": "warning"
}
```


### 11. Update Alert Rule
```
PUT /api/alerts/rules/{rule_id}
```


### 12. Delete Alert Rule
```
DELETE /api/alerts/rules/{rule_id}
```


### 13. Enable Alert
```
POST /api/alerts/{alert_id}/enable
```


### 14. Disable Alert
```
POST /api/alerts/{alert_id}/disable
```


### 15. Test Alert
```
POST /api/alerts/{alert_id}/test
```

**Response (200 OK):**
```json
{
  "alert_id": "alert-uuid",
  "test_event_id": "test-event-uuid",
  "notification_sent": true,
  "channels": {"email": "success", "slack": "success"}
}
```


### 16. Get Alert Summary
```
GET /api/alerts/summary
```

**Response (200 OK):**
```json
{
  "active_alerts": 5,
  "critical_count": 2,
  "warning_count": 3,
  "recent_events": [
    {
      "alert_id": "alert-uuid",
      "metric_name": "error_rate",
      "triggered_at": "2024-03-04T15:30:00Z"
    }
  ]
}
```


### 17-18. Additional Alert Endpoints

- `GET /api/alerts/anomaly-detection` - Get anomaly detection status
- `POST /api/alerts/bulk` - Create multiple alerts


---

## Custom Metrics Endpoints (8) {#custom-metrics-endpoints}

### 1. List Custom Metrics
```
GET /api/custom-metrics
```

**Response (200 OK):**
```json
{
  "metrics": [
    {
      "id": "custom-metric-uuid",
      "name": "Net Revenue Retention",
      "description": "Revenue increase from existing customers",
      "formula": "(current_mrr - churned_revenue + expansion_revenue) / previous_mrr",
      "components": ["current_mrr", "churned_revenue", "expansion_revenue"],
      "unit": "percent",
      "created_at": "2024-02-01T10:00:00Z"
    }
  ]
}
```


### 2. Create Custom Metric
```
POST /api/custom-metrics
```

**Request Body:**
```json
{
  "name": "Customer Health Score",
  "description": "Combined metric for customer health",
  "formula": "(usage_score * 0.4) + (support_tickets * -0.1) + (engagement_score * 0.5)",
  "components": ["usage_score", "support_tickets", "engagement_score"],
  "unit": "score"
}
```


### 3. Get Custom Metric
```
GET /api/custom-metrics/{metric_id}
```

**Response (200 OK):**
```json
{
  "id": "custom-metric-uuid",
  "name": "Customer Health Score",
  "formula": "(usage_score * 0.4) + (support_tickets * -0.1) + (engagement_score * 0.5)",
  "components": ["usage_score", "support_tickets", "engagement_score"],
  "calculation_count": 1250,
  "last_calculated": "2024-03-04T15:30:00Z"
}
```


### 4. Update Custom Metric
```
PUT /api/custom-metrics/{metric_id}
```

**Request Body:**
```json
{
  "formula": "(usage_score * 0.5) + (engagement_score * 0.5)",
  "components": ["usage_score", "engagement_score"]
}
```


### 5. Delete Custom Metric
```
DELETE /api/custom-metrics/{metric_id}
```


### 6. Calculate Custom Metric
```
POST /api/custom-metrics/{metric_id}/calculate
```

**Request Body:**
```json
{
  "components": {
    "usage_score": 85.5,
    "support_tickets": 2,
    "engagement_score": 92.0
  }
}
```

**Response (200 OK):**
```json
{
  "metric_id": "custom-metric-uuid",
  "result": 87.3,
  "components_used": 3,
  "calculation_time_ms": 45
}
```


### 7. Get Calculation History
```
GET /api/custom-metrics/{metric_id}/history
```

**Response (200 OK):**
```json
{
  "calculations": [
    {
      "timestamp": "2024-03-04T15:30:00Z",
      "result": 87.3,
      "components": {"usage_score": 85.5, "support_tickets": 2}
    }
  ]
}
```


### 8. Share Custom Metric
```
POST /api/custom-metrics/{metric_id}/share
```

**Request Body:**
```json
{
  "user_ids": ["user-2"],
  "group_ids": ["team-1"],
  "permission": "view"
}
```


---

## Queries Endpoints (13) {#queries-endpoints}

### 1. List Queries
```
GET /api/queries
```

**Response (200 OK):**
```json
{
  "queries": [
    {
      "id": "query-uuid",
      "name": "High Error Rate Services",
      "description": "Find services with error rate > 5%",
      "owner_user_id": "user-123",
      "created_at": "2024-02-01T10:00:00Z",
      "execution_count": 125
    }
  ]
}
```


### 2. Create Query
```
POST /api/queries
```

**Request Body:**
```json
{
  "name": "Revenue by Region",
  "description": "Total revenue breakdown by region",
  "sql": "SELECT region, SUM(revenue) FROM business_metrics GROUP BY region",
  "parameters": [
    {
      "name": "start_date",
      "type": "date",
      "default": "2024-03-01"
    }
  ]
}
```


### 3. Get Query
```
GET /api/queries/{query_id}
```

**Response (200 OK):**
```json
{
  "id": "query-uuid",
  "name": "Revenue by Region",
  "sql": "SELECT region, SUM(revenue) FROM business_metrics GROUP BY region",
  "parameters": [
    {"name": "start_date", "type": "date"}
  ],
  "created_at": "2024-02-01T10:00:00Z"
}
```


### 4. Update Query
```
PUT /api/queries/{query_id}
```


### 5. Delete Query
```
DELETE /api/queries/{query_id}
```


### 6. Execute Query
```
POST /api/queries/{query_id}/execute
```

**Request Body:**
```json
{
  "parameters": {
    "start_date": "2024-03-01",
    "end_date": "2024-03-04"
  },
  "timeout_seconds": 30
}
```

**Response (200 OK):**
```json
{
  "query_id": "query-uuid",
  "execution_id": "exec-uuid",
  "rows_returned": 25,
  "execution_time_ms": 145,
  "results": [
    {"region": "North America", "revenue": 250000},
    {"region": "Europe", "revenue": 180000}
  ]
}
```


### 7. Get Query Templates
```
GET /api/queries/templates
```

**Response (200 OK):**
```json
{
  "templates": [
    {
      "id": "template-1",
      "name": "Revenue Growth",
      "description": "Month-over-month revenue growth",
      "sql": "SELECT date, SUM(revenue) FROM metrics GROUP BY date"
    }
  ]
}
```


### 8. Get Execution History
```
GET /api/queries/{query_id}/history
```

**Response (200 OK):**
```json
{
  "executions": [
    {
      "execution_id": "exec-uuid",
      "executed_at": "2024-03-04T15:30:00Z",
      "execution_time_ms": 145,
      "rows_returned": 25,
      "status": "success"
    }
  ]
}
```


### 9. Share Query
```
POST /api/queries/{query_id}/share
```


### 10-13. Additional Query Endpoints

- `GET /api/queries/{id}/schema` - Get available schema
- `POST /api/queries/validate` - Validate query syntax
- `GET /api/queries/{id}/performance` - Get query performance metrics
- `POST /api/queries/{id}/duplicate` - Duplicate saved query


---

## Export Endpoints (15) {#export-endpoints}

### 1. Export Metrics
```
POST /api/export/metrics
```

**Request Body:**
```json
{
  "metric_names": ["mrr", "growth_rate", "churn_rate"],
  "start_time": "2024-03-01T00:00:00Z",
  "end_time": "2024-03-04T23:59:59Z",
  "format": "csv",
  "aggregate_by": "day"
}
```

**Response (202 Accepted):**
```json
{
  "export_id": "export-uuid",
  "status": "pending",
  "format": "csv",
  "estimated_size_kb": 2048
}
```


### 2. Export Dashboards
```
POST /api/export/dashboards
```

**Request Body:**
```json
{
  "dashboard_ids": ["dashboard-1", "dashboard-2"],
  "include_data": true,
  "format": "json"
}
```


### 3. Export Reports
```
POST /api/export/reports
```

**Request Body:**
```json
{
  "report_ids": ["report-1", "report-2"],
  "format": "pdf"
}
```


### 4. Get Export Status
```
GET /api/export/{export_id}
```

**Response (200 OK):**
```json
{
  "export_id": "export-uuid",
  "status": "completed",
  "format": "csv",
  "file_url": "/exports/export-uuid/metrics.csv",
  "file_size": 2097152,
  "completion_time": "2024-03-04T15:45:00Z",
  "expiration": "2024-03-11T15:45:00Z"
}
```


### 5. Download Export
```
GET /api/export/{export_id}/download
```

**Response (200 OK):** [Binary file content]


### 6. Create Bulk Export
```
POST /api/export/bulk
```

**Request Body:**
```json
{
  "exports": [
    {
      "type": "metrics",
      "metric_names": ["mrr", "growth_rate"],
      "format": "csv"
    },
    {
      "type": "dashboards",
      "dashboard_ids": ["dashboard-1"],
      "format": "json"
    }
  ]
}
```

**Response (202 Accepted):**
```json
{
  "bulk_export_id": "bulk-export-uuid",
  "export_ids": ["export-uuid-1", "export-uuid-2"],
  "status": "pending",
  "estimated_completion": "2024-03-04T16:00:00Z"
}
```


### 7. Get Supported Formats
```
GET /api/export/formats
```

**Response (200 OK):**
```json
{
  "formats": [
    {
      "name": "csv",
      "description": "Comma-separated values",
      "max_size_mb": 500,
      "compression": ["none", "gzip"]
    },
    {
      "name": "json",
      "description": "JSON format",
      "max_size_mb": 1000
    },
    {
      "name": "xlsx",
      "description": "Excel spreadsheet",
      "max_size_mb": 100
    },
    {
      "name": "pdf",
      "description": "PDF document",
      "max_size_mb": 50
    }
  ]
}
```


### 8. List Archives
```
GET /api/export/archives
```

**Response (200 OK):**
```json
{
  "archives": [
    {
      "archive_id": "archive-uuid",
      "created_at": "2024-03-04T15:45:00Z",
      "exports_count": 3,
      "total_size": 5242880,
      "expiration": "2024-03-11T15:45:00Z"
    }
  ]
}
```


### 9. Delete Archive
```
DELETE /api/export/archives/{archive_id}
```


### 10. Create Scheduled Export
```
POST /api/export/scheduled
```

**Request Body:**
```json
{
  "name": "Daily Metrics Export",
  "metric_names": ["mrr", "growth_rate"],
  "schedule": "daily",
  "time": "23:59",
  "format": "csv",
  "recipients": ["analytics@example.com"],
  "retention_days": 30
}
```


### 11. List Scheduled Exports
```
GET /api/export/scheduled
```


### 12. Update Scheduled Export
```
PUT /api/export/scheduled/{scheduled_id}
```


### 13. Delete Scheduled Export
```
DELETE /api/export/scheduled/{scheduled_id}
```


### 14-15. Additional Export Endpoints

- `POST /api/export/{id}/retry` - Retry failed export
- `POST /api/export/{id}/cancel` - Cancel pending export


---

## Data Models {#data-models}

### SystemMetric Model
**Purpose:** Multi-level time-series metrics aggregation

**Fields:**
- `id` (UUID): Primary identifier
- `tenant_id` (String): Tenant context
- `service_name` (String): Service identifier
- `metric_name` (String): Metric identifier
- `metric_type` (Enum): gauge, counter, histogram, timer
- `aggregation_level` (Enum): minute, hour, day, week, month, year
- `timestamp` (DateTime): Record timestamp
- `period_start` (DateTime): Aggregation period start
- `period_end` (DateTime): Aggregation period end
- `value` (Decimal): Primary metric value
- `min_value` (Decimal): Minimum value in period
- `max_value` (Decimal): Maximum value in period
- `created_at` (DateTime): Creation timestamp

**Indexes:**
- (tenant_id, service_name, timestamp)
- (metric_name, aggregation_level)
- (service_name, created_at)


### ServiceMetric Model
**Purpose:** Service performance tracking with percentiles

**Key Fields:**
- `response_time_p50` (Decimal): 50th percentile latency
- `response_time_p95` (Decimal): 95th percentile latency
- `response_time_p99` (Decimal): 99th percentile latency
- `response_time_avg` (Decimal): Average latency
- `total_requests` (Integer): Request count
- `successful_requests` (Integer): Successful count
- `failed_requests` (Integer): Failed count
- `error_rate` (Decimal): Error percentage
- `http_4xx_count` (Integer): 4xx status count
- `http_5xx_count` (Integer): 5xx status count
- `uptime_percent` (Decimal): Uptime percentage
- `cpu_percent` (Decimal): CPU usage
- `memory_percent` (Decimal): Memory usage
- `disk_percent` (Decimal): Disk usage


### UserActivityMetric Model
**Purpose:** User engagement and behavior analytics

**Key Fields:**
- `total_users` (Integer): Total user count
- `active_users` (Integer): Active user count
- `dau` (Integer): Daily Active Users
- `wau` (Integer): Weekly Active Users
- `mau` (Integer): Monthly Active Users
- `dau_wau_ratio` (Decimal): DAU/WAU engagement ratio
- `dau_mau_ratio` (Decimal): DAU/MAU engagement ratio
- `new_users` (Integer): New user count
- `returned_users` (Integer): Returning user count
- `churned_users` (Integer): Churned user count
- `total_sessions` (Integer): Session count
- `avg_session_duration` (Decimal): Average duration (seconds)
- `bounce_rate` (Decimal): Bounce rate percentage


### BusinessMetric Model
**Purpose:** Financial KPIs and business metrics

**Key Fields:**
- `mrr` (Decimal): Monthly Recurring Revenue
- `arr` (Decimal): Annual Recurring Revenue
- `revenue` (Decimal): Total revenue
- `total_customers` (Integer): Customer count
- `new_customers` (Integer): New customer count
- `churned_customers` (Integer): Churned customer count
- `churn_rate` (Decimal): Churn rate percentage
- `retention_rate` (Decimal): Retention rate percentage
- `ltv` (Decimal): Lifetime Value
- `cac` (Decimal): Customer Acquisition Cost
- `ltv_cac_ratio` (Decimal): LTV/CAC ratio
- `nrr` (Decimal): Net Revenue Retention
- `expansion_revenue` (Decimal): Expansion revenue
- `contraction_revenue` (Decimal): Contraction revenue
- `mom_growth` (Decimal): Month-over-month growth percentage
- `yoy_growth` (Decimal): Year-over-year growth percentage


### Dashboard Model
**Purpose:** Customizable analytics dashboards

**Fields:**
- `id` (UUID): Dashboard identifier
- `name` (String): Dashboard name
- `description` (String): Dashboard description
- `dashboard_type` (Enum): executive, operational, technical, custom
- `owner_user_id` (String): Owner user ID
- `is_public` (Boolean): Public visibility
- `widgets` (JSON Array): Widget configurations
- `refresh_interval` (Integer): Refresh interval (seconds)
- `view_count` (Integer): View count
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp


### Report Model
**Purpose:** Scheduled analytics reports

**Fields:**
- `id` (UUID): Report identifier
- `name` (String): Report name
- `description` (String): Report description
- `report_type` (Enum): summary, detailed, executive
- `metrics` (JSON Array): Included metrics
- `schedule` (String): Cron schedule pattern
- `recipients` (JSON Array): Email recipients
- `format` (String): PDF, XLSX, HTML, CSV
- `status` (Enum): draft, scheduled, generating, completed, archived
- `last_generated` (DateTime): Last generation time
- `created_at` (DateTime): Creation timestamp


### Alert Model
**Purpose:** Monitoring and threshold-based alerting

**Fields:**
- `id` (UUID): Alert identifier
- `metric_name` (String): Metric to monitor
- `condition_type` (Enum): threshold, anomaly, percent_change
- `threshold_value` (Decimal): Alert threshold
- `comparison_operator` (String): <, >, <=, >=, ==, !=
- `severity` (Enum): info, warning, critical, emergency
- `is_active` (Boolean): Alert activation status
- `evaluation_frequency` (String): 1m, 5m, 15m, 1h
- `notification_channels` (JSON Array): email, slack, webhook, sms
- `recipients` (JSON Array): Notification recipients
- `created_at` (DateTime): Creation timestamp
- `last_evaluated` (DateTime): Last evaluation time


### AlertEvent Model
**Purpose:** Alert lifecycle tracking

**Fields:**
- `id` (UUID): Event identifier
- `alert_id` (UUID): Associated alert ID
- `triggered_at` (DateTime): Event trigger time
- `metric_value` (Decimal): Metric value at trigger
- `threshold_value` (Decimal): Threshold value
- `severity` (Enum): info, warning, critical, emergency
- `status` (Enum): active, acknowledged, resolved
- `acknowledged_at` (DateTime): Acknowledgment time
- `acknowledged_by` (String): User who acknowledged
- `resolved_at` (DateTime): Resolution time
- `resolution_notes` (String): Resolution notes


### CustomMetric Model
**Purpose:** User-defined metric formulas

**Fields:**
- `id` (UUID): Metric identifier
- `name` (String): Metric name
- `description` (String): Metric description
- `formula` (String): Formula expression
- `components` (JSON Array): Component metric names
- `unit` (String): Measurement unit
- `created_at` (DateTime): Creation timestamp


### AnalyticsQuery Model
**Purpose:** Saved analytics queries

**Fields:**
- `id` (UUID): Query identifier
- `name` (String): Query name
- `description` (String): Query description
- `sql` (String): SQL query content
- `parameters` (JSON Array): Query parameters
- `created_at` (DateTime): Creation timestamp
- `execution_count` (Integer): Number of executions


---

## Configuration {#configuration}

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/analytics

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 days

# Application
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=INFO

# Rate Limiting
RATELIMIT_ENABLED=True
RATELIMIT_DEFAULT=100/hour

# Data Retention (days)
METRIC_RETENTION_MINUTE=7
METRIC_RETENTION_HOUR=30
METRIC_RETENTION_DAY=365
METRIC_RETENTION_MONTH=2555  # ~7 years
METRIC_RETENTION_YEAR=3650   # 10 years
```


### Config Classes

**DevelopmentConfig:**
- Debug: True
- Testing: False
- Database: PostgreSQL (dev)
- Rate Limiting: Disabled

**TestingConfig:**
- Debug: False
- Testing: True
- Database: SQLite (in-memory)
- Rate Limiting: Disabled

**ProductionConfig:**
- Debug: False
- Testing: False
- Database: PostgreSQL (production)
- Rate Limiting: Enabled
- SSL: Required


---

## Error Handling {#error-handling}

### Standard Error Response

```json
{
  "error": {
    "code": "INVALID_METRICS_FILTER",
    "message": "Invalid metric filter provided",
    "status_code": 400,
    "details": {
      "invalid_fields": ["metric_names"],
      "suggestion": "Check provided metric names"
    },
    "request_id": "req-uuid",
    "timestamp": "2024-03-04T15:30:00Z"
  }
}
```


### Common Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| INVALID_REQUEST | 400 | Malformed request |
| MISSING_AUTH | 401 | Missing authentication |
| INVALID_TOKEN | 401 | Invalid token |
| INSUFFICIENT_PERMISSIONS | 403 | Insufficient permissions |
| RESOURCE_NOT_FOUND | 404 | Resource not found |
| RESOURCE_CONFLICT | 409 | Resource conflict |
| RATE_LIMIT_EXCEEDED | 429 | Rate limit exceeded |
| SERVICE_UNAVAILABLE | 503 | Service unavailable |
| DATABASE_ERROR | 500 | Database error |
| UNKNOWN_ERROR | 500 | Unknown error |


---

## Rate Limiting {#rate-limiting}

### Default Limits

- General API: 100 requests/hour
- Metrics Endpoint: 500 requests/hour
- Export Endpoint: 50 requests/hour
- Query Endpoint: 100 requests/hour

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1677127056
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "retry_after": 3600
  }
}
```


---

## Deployment Guide {#deployment}

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=main.py
ENV FLASK_ENV=production

EXPOSE 5009
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5009", "main:app"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  analytics-db:
    image: postgres:14
    environment:
      POSTGRES_DB: analytics
      POSTGRES_USER: analytics
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - analytics_db:/var/lib/postgresql/data

  analytics-cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  analytics-service:
    build: .
    ports:
      - "5009:5009"
    environment:
      DATABASE_URL: postgresql://analytics:secure_password@analytics-db:5432/analytics
      REDIS_URL: redis://analytics-cache:6379
      FLASK_ENV: production
    depends_on:
      - analytics-db
      - analytics-cache

volumes:
  analytics_db:
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: analytics-service
  template:
    metadata:
      labels:
        app: analytics-service
    spec:
      containers:
      - name: analytics
        image: analytics-service:latest
        ports:
        - containerPort: 5009

        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: analytics-secrets
              key: database-url
        - name: REDIS_URL
          value: redis://cache-service:6379
        - name: FLASK_ENV
          value: production

        livenessProbe:
          httpGet:
            path: /health
            port: 5009
          initialDelaySeconds: 30
          periodSeconds: 10

        readinessProbe:
          httpGet:
            path: /health
            port: 5009
          initialDelaySeconds: 10
          periodSeconds: 5

        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
```


---

## Troubleshooting {#troubleshooting}

### Common Issues

**Issue: Database Connection Timeout**
```
Solution: Check PostgreSQL is running and DATABASE_URL is correct
Test: psql $DATABASE_URL -c "SELECT 1"
```

**Issue: Redis Connection Refused**
```
Solution: Verify Redis is running on configured port
Test: redis-cli ping
```

**Issue: JWT Token Expired**
```
Solution: Refresh token using /auth/refresh endpoint
Response: Get new access token
```

**Issue: Tenant ID Mismatch**
```
Solution: Verify X-Tenant-ID header matches authenticated tenant
Test: Check JWT payload tenant_id
```

**Issue: Rate Limit Exceeded**
```
Solution: Implement exponential backoff with jitter
Wait: Check X-RateLimit-Reset header
```

### Monitoring

**Key Metrics to Monitor:**
- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database query time
- Redis hit ratio
- JWT token issuance rate

**Health Check Endpoint:**
```bash
curl http://localhost:5009/health
```

**Metrics Endpoint:**
```bash
curl http://localhost:5009/metrics
```

### Performance Tuning

1. **Database**: Increase connection pool (default: 10-20)
2. **Redis**: Use pipelining for bulk operations  
3. **Caching**: Adjust TTLs based on query patterns
4. **Indexes**: Ensure strategic indexes exist on high-cardinality columns
5. **Workers**: Scale Gunicorn workers based on CPU cores

---

## Next Steps

1. Review security best practices
2. Implement monitoring and alerting
3. Set up automated backups
4. Plan capacity requirements
5. Document operational procedures

For support: analytics-team@company.com
"""

import json

# Generate API documentation JSON
documentation = {
    "service": "analytics-service",
    "version": "1.0.0",
    "port": 5009,
    "endpoints": {
        "metrics": {
            "count": 15,
            "modules": ["GET", "POST", "PUT", "DELETE"],
            "examples": [
                "GET /api/metrics/system",
                "GET /api/metrics/service",
                "GET /api/metrics/activity",
                "GET /api/metrics/business"
            ]
        },
        "dashboards": {
            "count": 17,
            "modules": ["Dashboard CRUD", "Widget Management", "Sharing"],
            "examples": [
                "GET /api/dashboards",
                "POST /api/dashboards",
                "GET /api/dashboards/{id}/widgets"
            ]
        },
        "reports": {
            "count": 15,
            "modules": ["Report CRUD", "Generation", "Scheduling"],
            "examples": [
                "POST /api/reports/{id}/generate",
                "GET /api/reports/{id}/download/{gen_id}"
            ]
        },
        "alerts": {
            "count": 18,
            "modules": ["Alert CRUD", "Events", "Rules"],
            "examples": [
                "GET /api/alerts",
                "POST /api/alerts/{id}/events/{event_id}/acknowledge"
            ]
        },
        "custom_metrics": {
            "count": 8,
            "modules": ["Metrics CRUD", "Calculation", "Sharing"],
            "examples": [
                "POST /api/custom-metrics/{id}/calculate"
            ]
        },
        "queries": {
            "count": 13,
            "modules": ["Query CRUD", "Execution", "Templates"],
            "examples": [
                "POST /api/queries/{id}/execute"
            ]
        },
        "export": {
            "count": 15,
            "modules": ["Data Export", "Bulk Export", "Scheduled"],
            "examples": [
                "POST /api/export/metrics",
                "GET /api/export/{id}/download"
            ]
        }
    },
    "models": {
        "system_metric": {"fields": 14, "indexes": 3},
        "service_metric": {"fields": 14, "indexes": 3},
        "user_activity_metric": {"fields": 13, "indexes": 2},
        "business_metric": {"fields": 16, "indexes": 3},
        "dashboard": {"fields": 11, "indexes": 2},
        "report": {"fields": 11, "indexes": 2},
        "alert": {"fields": 12, "indexes": 3},
        "alert_event": {"fields": 11, "indexes": 2},
        "custom_metric": {"fields": 7, "indexes": 1},
        "analytics_query": {"fields": 8, "indexes": 1}
    },
    "statistics": {
        "total_endpoints": 101,
        "total_models": 10,
        "total_enums": 8,
        "total_indexes": 25,
        "authentication": "JWT with tenant context",
        "rate_limiting": "100/hour default",
        "caching": "Redis with configurable TTLs"
    }
}

if __name__ == '__main__':
    print(json.dumps(documentation, indent=2))
