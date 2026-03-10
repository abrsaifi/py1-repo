# DocPro Failover Strategy & High Availability

## Overview

This document defines the failover strategy and high availability approach for DocPro on production infrastructure.

---

## Architecture

### Pre-Failover (Single Server)
```
Internet
  ↓
[Nginx Reverse Proxy]
  ↓
[Flask App Server] ← Single point of failure
  ↓
[PostgreSQL] + [Redis]
```

### Post-Failover (HA Configuration)
```
Internet
  ↓
[Nginx Load Balancer] ← Multiple instances
  ↓
[Flask Pool: 3+ instances with health checks]
  ↓
[PostgreSQL Primary + Replica] + [Redis Cluster]
```

---

## Health Check Strategy

### Check Frequency
- **Load Balancer**: Every 10 seconds to all backends
- **Readiness**: Every 5 seconds (Kubernetes)
- **Liveness**: Every 30 seconds (Kubernetes)
- **Startup**: One-time on container start

### Health Check Endpoints

**Basic Check** (1-2ms)
```
GET /health
Response: 200 OK if alive
```

**Detailed Check** (10-50ms)
```
GET /health/detailed
Checks: Database, Redis, Celery
Response: 503 if critical component down
```

**Kubernetes Probes**
```
Readiness:  GET /health/readiness  (5s interval)
Liveness:   GET /health/liveness   (30s interval)
Startup:    GET /health/startup    (one-time)
```

### Failure Detection
1. **3 consecutive failures** → Server marked unhealthy
2. **2 consecutive successes** → Server marked healthy again
3. **Timeout = 30 seconds** → Auto-exclude from rotation

---

## Failover Scenarios

### Scenario 1: Single Backend Fails

**Initial State**
```
Frontend → Nginx → [Flask-1: healthy, Flask-2: healthy, Flask-3: healthy]
```

**Failure Detection**
```
t=0s:   Flask-2 crashes
t=10s:  First health check fails
t=20s:  Second health check fails
t=30s:  Third health check fails → Flask-2 removed from pool
```

**Recovery**
```
Nginx continues routing to Flask-1 and Flask-3
No user-facing interruption (assuming traffic < 50% of capacity)
```

**Removal from Load Balancer**
```nginx
upstream docpro_backend {
    server flask_app_1:5000;
    # server flask_app_2:5000;  ← Removed by health check
    server flask_app_3:5000;
}
```

### Scenario 2: Database Replication Failover

**Initial State**
```
Primary DB (RW) → Replica-1 (RO) → Replica-2 (RO)
All backends reading from replicas, writing to primary
```

**Primary Database Fails**
```
t=0s:   Writes to primary fail
t=5s:   Connection pool notices stale connection
t=10s:  Health checks detect DB unavailability
t=15s:  Trigger failover: Replica-1 promoted to primary
```

**Failover Execution**
```
1. Stop accepting writes to old primary
2. Promote Replica-1 to primary
3. Point write connections to Replica-1
4. Resync other replicas
5. Resume operations
```

**Recovery Window**: 30-60 seconds (RTO)
**Data Loss**: 0 (RPO) if synchronous replication

### Scenario 3: Redis Cluster Failover

**Initial State**
```
Redis Master → Redis Slave [async replication]
Cache and session storage
```

**Redis Master Fails**
```
t=0s:   Cache writes fail
t=5s:   Flask detects Redis unavailability
t=10s:  Mark Redis as degraded
t=15s:  Continue operation without cache (slow mode)
```

**Manual Failover**
```
redis-cli --replica 127.0.0.1:6380 SLAVEOF 127.0.0.1:6379
# Promote slave to master
```

**Recovery Window**: Cache not available until manual intervention
**Data Loss**: Recent cache entries may be lost

### Scenario 4: Nginx Load Balancer Fails

**Initial State**
```
[Primary Nginx] ← All traffic
[Backup Nginx] (standby with keepalived)
```

**Nginx Fails**
```
t=0s:   Keepalived detects primary failure
t=2s:   VIP (virtual IP) moves to backup Nginx
t=3s:   Traffic resumes via backup
```

**Configuration with Keepalived**
```
Virtual IP: 203.0.113.10
Primary:    203.0.113.11 (active)
Secondary:  203.0.113.12 (standby)

When primary fails, VIP moves to secondary
Users see no interruption (DNS/IP cached <30s)
```

---

## Circuit Breaker Pattern

Used to prevent cascading failures.

### States

**CLOSED (Normal)**
- Requests pass through normally
- Errors are counted

**OPEN (Circuit Broken)**
- Requests fail immediately without attempting backend
- Prevents overwhelming failing service
- Waits for recovery timeout

**HALF-OPEN (Recovery Test)**
- Limited requests sent to test recovery
- If successful → CLOSED
- If failed → OPEN

### Implementation

```python
from app.load_balancer_config import CircuitBreaker

# Per-server circuit breaker
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

if breaker.can_attempt_request():
    try:
        response = proxy_request(server)
        breaker.record_success()
    except Exception as e:
        breaker.record_failure()
        if not breaker.can_attempt_request():
            return "Service Temporarily Unavailable"
```

---

## Session Affinity (Sticky Sessions)

### Cookie-Based Affinity

**Request 1**
```
Client → Nginx → Flask-1
Response includes: Set-Cookie: srv_route=flask_1
```

**Request 2**
```
Client (remembers srv_route=flask_1)
→ Nginx (reads cookie, routes to Flask-1)
→ Flask-1
```

### Benefits
- Local session data stays on same server
- Better cache locality
- Reduced session replication

### Drawbacks
- Uneven load distribution if user disconnects/reconnects
- Single server failure loses session

### Configuration in Nginx

```nginx
# Sticky sessions using route header
upstream docpro_backend {
    sticky route $route_id cookie srv_route expires=1h httponly secure;
    
    server flask_app_1:5000 route=r1;
    server flask_app_2:5000 route=r2;
    server flask_app_3:5000 route=r3;
}
```

---

## Monitoring & Alerting

### Metrics to Monitor

**Application Level**
- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Response time by endpoint
- Cache hit rate

**Infrastructure Level**
- CPU usage per server
- Memory usage per server
- Disk I/O
- Network throughput

**Database Level**
- Connection count
- Query latency
- Replication lag
- Index usage

**Cache Level**
- Hit rate
- Memory usage
- Eviction rate

### Alert Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Node down | Any failure | Page on-call |
| CPU > 80% | 5+ minutes | Auto-scale up |
| Memory > 85% | Persistent | Page on-call |
| Error rate > 1% | 2+ minutes | Page on-call |
| Latency p99 > 1s | 5+ minutes | Investigate |
| Replication lag > 10s | Any | Page on-call |

### Alert Channels
- PagerDuty (critical)
- Slack (warning/info)
- Email (digest daily)

---

## Disaster Recovery Plan

### RTO & RPO Targets

```
RTO (Recovery Time Objective):
- Single server failure: 0 seconds (automatic failover)
- Database failure: 60 seconds (manual failover)
- Full data center: 15 minutes (switch region)

RPO (Recovery Point Objective):
- Database: 0 (synchronous replication)
- Cache: 5 minutes (can be lost)
- Backups: 24 hours (point in time recovery)
```

### Backup Strategy

**Database**
```
- Continuous WAL archiving to S3
- Daily full backup at 2 AM UTC
- 30-day retention
- Test restore quarterly
```

**Code & Configuration**
```
- All code in Git with tags
- Environment files encrypted in separate secure storage
- Terraform/Docker-compose for IaC
- Version control all infrastructure
```

**Secrets**
```
- Stored in AWS Secrets Manager / HashiCorp Vault
- Encrypted at rest
- Audit logged
- Rotated monthly
```

### Recovery Procedures

**Database Recovery**
```
1. Stop writes to current primary
2. Examine last good backup timestamp
3. Restore to point-in-time from WAL
4. Verify data integrity
5. Point replicas to new primary
6. Resume service
```

**Full Application Recovery**
```
1. Check backup inventory
2. Restore database from backup
3. Restore code from Git tag
4. Restore environment from encrypted config
5. Run migrations
6. Warm up cache
7. Health check all endpoints
8. Switch DNS to new instance
```

---

## Testing & Drills

### Monthly Failover Tests
- Manually trigger database failover
- Verify replication catches up
- Test backup restoration
- Document time taken

### Quarterly Disaster Recovery Drills
- Stage recovery in non-production
- Practice full application recovery
- Time the entire process
- Update runbooks

### Annual Full Simulation
- Simulate complete data center loss
- Recover to alternate location
- Verify all services operational
- Document lessons learned

---

## Communication Plan

### During Incident

**Internal (first alert)**
- Post to #incident-response Slack
- @ mention on-call engineer
- Create P1/P2/P3 tag

**To Customers (after 5 minutes if ongoing)**
- Email to status page
- Post incident update every 15 minutes
- Include ETA for resolution
- Link to status.docpro.io

**Post-Incident Review**
- Hold within 48 hours
- Document timeline
- Identify root cause
- Create action items
- Share public post-mortem (if appropriate)

---

## Runbooks

### When Flask App Goes Down

1. Check health endpoint: `curl https://docpro.example.com/health/detailed`
2. Check logs: `kubectl logs -f deployment/flask-app`
3. Check resource usage: `kubectl top pods`
4. If resource exhaustion:
   - Scale up: `kubectl scale deployment flask-app --replicas=5`
5. If application error:
   - Rollback to previous version: `kubectl rollout undo deployment/flask-app`
6. Verify recovery: `curl https://docpro.example.com/health`

### When Database Goes Down

1. Check replication status: `SHOW SLAVE STATUS\G` (MySQL/PostgreSQL equivalent)
2. Check backup availability: AWS RDS console → automated backups
3. Determine RPO (latest backup): Should be < 1 hour
4. Promote read replica: AWS RDS → Promote Read Replica
5. Update connection string in app config
6. Verify app connectivity: Check application logs
7. Promote other replicas once primary stabilizes

### When Redis Goes Down

1. Check Redis health: `redis-cli ping`
2. Check memory usage: `redis-cli info memory`
3. If high memory:
   - Check for leaks: `redis-cli --bigkeys`
   - Evict oldest keys if needed: `redis-cli config set maxmemory-policy allkeys-lru`
4. If crashed:
   - Restart: `systemctl restart redis` or `docker restart redis`
   - Cache layer will rebuild automatically
   - Performance will be degraded until warmed
5. Verify recovery: Check cache hit rate in analytics

---

## Configuration Examples

### Docker Compose (Multi-Container HA)

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - flask_1
      - flask_2
      - flask_3

  flask_1:
    build: .
    environment:
      - FLASK_APP=app
      - FLASK_ENV=production
    expose:
      - 5000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  flask_2:
    build: .
    # ... same as flask_1

  flask_3:
    build: .
    # ... same as flask_1

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  postgres_data:
```

---

## Summary

- **Automatic Detection**: Health checks every 10s
- **Quick Failover**: <30s to remove failed server
- **No Manual Intervention**: For single server failures
- **Database Resilience**: Replicas + WAL archiving
- **Testing**: Monthly failover tests, quarterly DR drills
- **Communication**: Alerts and status page updates

---

**Last Updated**: 2024-01-15
**Review Schedule**: Q1, Q3 annually
**Emergency Contacts**: See separate runbook
