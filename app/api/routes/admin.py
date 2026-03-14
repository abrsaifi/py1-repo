"""Admin API routes for system management."""
import csv
import hashlib
import hmac
import ipaddress
import json
import os
import secrets
from collections import Counter
from io import BytesIO, StringIO

from flask import Blueprint, current_app, request, jsonify, send_file
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, or_, text
from app.models import db, User, Conversion, Subscription, APIKey, BillingAuditLog, BillingInvoice, UserSession
from app.middleware.auth import admin_required
from app.services.subscription_service import SubscriptionService

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

DEFAULT_INVOICE_PAGE_SIZE = 10
DEFAULT_AUDIT_PAGE_SIZE = 25
MAX_BILLING_PAGE_SIZE = 100


def _admin_now():
    return datetime.now(timezone.utc)


def _admin_state_file_path():
    state_dir = os.path.join(current_app.instance_path, 'admin-state')
    os.makedirs(state_dir, exist_ok=True)
    return os.path.join(state_dir, 'dashboard-state.json')


def _admin_time_plus(**kwargs):
    return (_admin_now() + timedelta(**kwargs)).isoformat()


def _create_default_admin_state():
    return {
        'version': 1,
        'automation': {
            'workflows': [
                {
                    'id': 'WF-001',
                    'name': 'Daily SEO Page Generator',
                    'type': 'SEO',
                    'status': 'running',
                    'executions': 847,
                    'lastRunAt': _admin_time_plus(hours=-8),
                    'nextRunAt': _admin_time_plus(hours=10),
                    'realtime': False,
                    'description': 'Generates SEO landing pages and indexing payloads.',
                },
                {
                    'id': 'WF-002',
                    'name': 'Keyword Ranking Checker',
                    'type': 'SEO',
                    'status': 'running',
                    'executions': 156,
                    'lastRunAt': _admin_time_plus(minutes=-20),
                    'nextRunAt': _admin_time_plus(hours=2),
                    'realtime': False,
                    'description': 'Checks indexed keyword movements and snapshots changes.',
                },
                {
                    'id': 'WF-003',
                    'name': 'Sitemap Auto-Submit',
                    'type': 'SEO',
                    'status': 'running',
                    'executions': 52,
                    'lastRunAt': _admin_time_plus(hours=-12),
                    'nextRunAt': _admin_time_plus(hours=14),
                    'realtime': False,
                    'description': 'Publishes sitemap updates after content and metadata changes.',
                },
                {
                    'id': 'WF-004',
                    'name': 'Conversion Success Email',
                    'type': 'Email',
                    'status': 'running',
                    'executions': 3421,
                    'lastRunAt': _admin_time_plus(minutes=-5),
                    'nextRunAt': None,
                    'realtime': True,
                    'description': 'Sends completion notifications when conversions succeed.',
                },
                {
                    'id': 'WF-005',
                    'name': 'Daily Report Newsletter',
                    'type': 'Email',
                    'status': 'running',
                    'executions': 24,
                    'lastRunAt': _admin_time_plus(hours=-6),
                    'nextRunAt': _admin_time_plus(hours=18),
                    'realtime': False,
                    'description': 'Builds and distributes a daily operational digest.',
                },
                {
                    'id': 'WF-006',
                    'name': 'User Signup Welcome',
                    'type': 'Email',
                    'status': 'running',
                    'executions': 1247,
                    'lastRunAt': _admin_time_plus(minutes=-30),
                    'nextRunAt': None,
                    'realtime': True,
                    'description': 'Delivers onboarding email after account creation.',
                },
                {
                    'id': 'WF-007',
                    'name': 'High Error Rate Alert',
                    'type': 'Alert',
                    'status': 'running',
                    'executions': 12,
                    'lastRunAt': _admin_time_plus(hours=-1),
                    'nextRunAt': None,
                    'realtime': True,
                    'description': 'Escalates conversion failure spikes for operator review.',
                },
                {
                    'id': 'WF-008',
                    'name': 'Storage Quota Warning',
                    'type': 'Alert',
                    'status': 'paused',
                    'executions': 0,
                    'lastRunAt': _admin_time_plus(days=-2),
                    'nextRunAt': None,
                    'realtime': True,
                    'description': 'Warns operators when storage thresholds are crossed.',
                },
                {
                    'id': 'WF-009',
                    'name': 'Rate Limit Exceeded Alert',
                    'type': 'Alert',
                    'status': 'failed',
                    'executions': 8,
                    'lastRunAt': _admin_time_plus(hours=-3),
                    'nextRunAt': _admin_time_plus(hours=1),
                    'realtime': False,
                    'description': 'Captures burst abuse and surfaces repeat offenders.',
                },
                {
                    'id': 'WF-010',
                    'name': 'Failed Conversion Alert',
                    'type': 'Alert',
                    'status': 'running',
                    'executions': 67,
                    'lastRunAt': _admin_time_plus(minutes=-10),
                    'nextRunAt': None,
                    'realtime': True,
                    'description': 'Flags failed jobs for support and incident review.',
                },
            ],
            'logs': [
                {
                    'id': f"log-{secrets.token_hex(4)}",
                    'workflowId': 'WF-001',
                    'timestamp': _admin_time_plus(hours=-8),
                    'level': 'info',
                    'message': 'Workflow completed and published 42 page artifacts.',
                    'status': 'success',
                },
                {
                    'id': f"log-{secrets.token_hex(4)}",
                    'workflowId': 'WF-007',
                    'timestamp': _admin_time_plus(hours=-1),
                    'level': 'warning',
                    'message': 'Error-rate threshold reached 6.2% in the last 24 hours.',
                    'status': 'warning',
                },
                {
                    'id': f"log-{secrets.token_hex(4)}",
                    'workflowId': 'WF-009',
                    'timestamp': _admin_time_plus(hours=-3),
                    'level': 'error',
                    'message': 'Webhook dispatch to alert channel failed and is queued for retry.',
                    'status': 'failed',
                },
            ],
        },
        'reportScheduling': {
            'schedules': [
                {
                    'id': 'SCH-001',
                    'reportName': 'Daily Operations Summary',
                    'frequency': 'daily',
                    'time': '08:00',
                    'recipients': ['ops@docpro.local', 'support@docpro.local'],
                    'format': 'pdf',
                    'enabled': True,
                    'includeCharts': True,
                    'createdAt': _admin_time_plus(days=-20),
                    'updatedAt': _admin_time_plus(days=-1),
                    'lastRunAt': _admin_time_plus(days=-1, hours=-2),
                    'nextRunAt': _admin_time_plus(hours=18),
                    'testSentAt': None,
                },
                {
                    'id': 'SCH-002',
                    'reportName': 'Weekly Billing Exceptions',
                    'frequency': 'weekly',
                    'time': '09:30',
                    'recipients': ['finance@docpro.local'],
                    'format': 'csv',
                    'enabled': True,
                    'includeCharts': False,
                    'createdAt': _admin_time_plus(days=-35),
                    'updatedAt': _admin_time_plus(days=-7),
                    'lastRunAt': _admin_time_plus(days=-6),
                    'nextRunAt': _admin_time_plus(days=1),
                    'testSentAt': _admin_time_plus(days=-14),
                },
            ],
        },
        'security': {
            'rateLimit': {
                'defaultLimit': 1000,
                'windowSize': '1 hour',
                'burstAllowance': 200,
                'updatedAt': _admin_now().isoformat(),
            },
            'blockedIps': [
                {
                    'id': 'BLK-001',
                    'ip': '203.45.67.89',
                    'reason': 'Rate limit exceeded',
                    'blockedDate': _admin_time_plus(hours=-20),
                    'severity': 'high',
                    'source': 'automatic',
                },
                {
                    'id': 'BLK-002',
                    'ip': '158.92.134.56',
                    'reason': 'Suspicious pattern',
                    'blockedDate': _admin_time_plus(days=-1),
                    'severity': 'medium',
                    'source': 'automatic',
                },
                {
                    'id': 'BLK-003',
                    'ip': '210.100.88.34',
                    'reason': 'SQL injection attempt',
                    'blockedDate': _admin_time_plus(days=-2),
                    'severity': 'critical',
                    'source': 'automatic',
                },
            ],
            'violations': [
                {
                    'id': 'VIO-001',
                    'ip': '10.20.30.40',
                    'endpoint': '/api/convert',
                    'count': 2847,
                    'limit': 1000,
                    'timestamp': _admin_time_plus(minutes=-25),
                    'status': 'active',
                    'reason': 'Burst traffic exceeded hourly policy.',
                },
                {
                    'id': 'VIO-002',
                    'ip': '192.168.50.10',
                    'endpoint': '/api/upload',
                    'count': 1567,
                    'limit': 500,
                    'timestamp': _admin_time_plus(minutes=-40),
                    'status': 'active',
                    'reason': 'Upload storm tripped abuse protection.',
                },
                {
                    'id': 'VIO-003',
                    'ip': '172.30.20.15',
                    'endpoint': '/api/health',
                    'count': 892,
                    'limit': 5000,
                    'timestamp': _admin_time_plus(hours=-2),
                    'status': 'resolved',
                    'reason': 'Temporary probe spike self-resolved.',
                },
            ],
        },
        'activityEvents': [],
    }


def _load_admin_state():
    state_path = _admin_state_file_path()
    if not os.path.exists(state_path):
        state = _create_default_admin_state()
        _save_admin_state(state)
        return state

    try:
        with open(state_path, 'r', encoding='utf-8') as handle:
            state = json.load(handle)
    except (OSError, ValueError):
        state = _create_default_admin_state()
        _save_admin_state(state)
        return state

    default_state = _create_default_admin_state()
    state.setdefault('version', default_state['version'])
    state.setdefault('automation', default_state['automation'])
    state['automation'].setdefault('workflows', default_state['automation']['workflows'])
    state['automation'].setdefault('logs', default_state['automation']['logs'])
    state.setdefault('reportScheduling', default_state['reportScheduling'])
    state['reportScheduling'].setdefault('schedules', default_state['reportScheduling']['schedules'])
    state.setdefault('security', default_state['security'])
    state['security'].setdefault('rateLimit', default_state['security']['rateLimit'])
    state['security'].setdefault('blockedIps', default_state['security']['blockedIps'])
    state['security'].setdefault('violations', default_state['security']['violations'])
    state.setdefault('activityEvents', [])
    return state


def _save_admin_state(state):
    state_path = _admin_state_file_path()
    temp_path = f'{state_path}.tmp'
    with open(temp_path, 'w', encoding='utf-8') as handle:
        json.dump(state, handle, indent=2)
    os.replace(temp_path, state_path)


def _append_admin_state_activity_event(state, action, resource_type, resource_id, resource_name, details=None, severity='info', status='success', user_name='admin'):
    state.setdefault('activityEvents', []).append({
        'id': f'admin-state-{action}-{secrets.token_hex(4)}',
        'timestamp': _admin_now().isoformat(),
        'action': action,
        'userId': '',
        'userName': user_name,
        'resourceType': resource_type,
        'resourceId': str(resource_id),
        'resourceName': resource_name,
        'status': status,
        'severity': severity,
        'details': details or {},
        'source': 'admin_state',
    })
    state['activityEvents'] = sorted(
        state['activityEvents'],
        key=lambda item: item.get('timestamp') or '',
        reverse=True,
    )[:500]


def _append_workflow_log(state, workflow_id, level, message, status='success'):
    state.setdefault('automation', {}).setdefault('logs', []).append({
        'id': f'log-{secrets.token_hex(4)}',
        'workflowId': workflow_id,
        'timestamp': _admin_now().isoformat(),
        'level': level,
        'message': message,
        'status': status,
    })
    state['automation']['logs'] = sorted(
        state['automation']['logs'],
        key=lambda item: item.get('timestamp') or '',
        reverse=True,
    )[:500]


def _parse_state_timestamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).replace(tzinfo=None)
    except ValueError:
        return None


def _format_state_timestamp(value):
    parsed = _parse_state_timestamp(value) if isinstance(value, str) else value
    return _format_admin_datetime(parsed)


def _format_next_run_label(next_run_at, realtime=False, status=None):
    if status == 'paused':
        return 'Paused'
    if realtime:
        return 'Real-time'
    if not next_run_at:
        return 'Not scheduled'
    return _format_state_timestamp(next_run_at) or 'Not scheduled'


def _calculate_schedule_next_run(frequency, time_value):
    now = _admin_now()
    try:
        hour_value, minute_value = [int(part) for part in time_value.split(':', 1)]
    except (TypeError, ValueError):
        hour_value, minute_value = 9, 0

    next_run = now.replace(hour=hour_value, minute=minute_value, second=0, microsecond=0)
    if next_run <= now:
        if frequency == 'weekly':
            next_run += timedelta(days=7)
        elif frequency == 'monthly':
            next_run += timedelta(days=30)
        else:
            next_run += timedelta(days=1)
    elif frequency == 'weekly':
        next_run += timedelta(days=7 if next_run.date() != now.date() else 0)
    elif frequency == 'monthly':
        next_run += timedelta(days=30 if next_run.date() != now.date() else 0)

    return next_run.isoformat()


def _serialize_admin_workflow(workflow, logs_by_workflow=None):
    logs = logs_by_workflow.get(workflow['id'], []) if logs_by_workflow else []
    return {
        **workflow,
        'lastRun': _format_state_timestamp(workflow.get('lastRunAt')),
        'nextRun': _format_next_run_label(workflow.get('nextRunAt'), workflow.get('realtime'), workflow.get('status')),
        'logCount': len(logs),
        'lastLogLevel': logs[0]['level'] if logs else None,
    }


def _build_automation_payload():
    state = _load_admin_state()
    workflows = state.get('automation', {}).get('workflows', [])
    workflow_logs = state.get('automation', {}).get('logs', [])
    logs_by_workflow = {}
    for entry in workflow_logs:
        logs_by_workflow.setdefault(entry.get('workflowId'), []).append(entry)

    serialized_workflows = [_serialize_admin_workflow(workflow, logs_by_workflow) for workflow in workflows]
    type_counts = Counter((workflow.get('type') or 'Other').lower() for workflow in workflows if workflow.get('status') == 'running')

    return {
        'generatedAt': _admin_now().isoformat(),
        'stats': {
            'activeWorkflows': sum(1 for workflow in workflows if workflow.get('status') == 'running'),
            'seoAutomation': type_counts.get('seo', 0),
            'emailAutomation': type_counts.get('email', 0),
            'alertAutomation': type_counts.get('alert', 0),
            'pausedWorkflows': sum(1 for workflow in workflows if workflow.get('status') == 'paused'),
            'failedWorkflows': sum(1 for workflow in workflows if workflow.get('status') == 'failed'),
        },
        'workflows': serialized_workflows,
    }


def _validate_email_recipients(recipients):
    validated = []
    for recipient in recipients or []:
        email_value = (recipient or '').strip().lower()
        if not email_value or '@' not in email_value or '.' not in email_value.split('@')[-1]:
            raise ValueError(f'Invalid recipient email: {recipient}')
        validated.append(email_value)
    return validated


def _serialize_report_schedule(schedule):
    return {
        **schedule,
        'createdAt': _format_state_timestamp(schedule.get('createdAt')),
        'updatedAt': _format_state_timestamp(schedule.get('updatedAt')),
        'lastRun': _format_state_timestamp(schedule.get('lastRunAt')),
        'nextRun': _format_state_timestamp(schedule.get('nextRunAt')) if schedule.get('enabled') else 'Disabled',
        'testSentAt': _format_state_timestamp(schedule.get('testSentAt')),
    }


def _build_report_schedules_payload():
    state = _load_admin_state()
    schedules = state.get('reportScheduling', {}).get('schedules', [])
    active_count = sum(1 for schedule in schedules if schedule.get('enabled'))
    return {
        'generatedAt': _admin_now().isoformat(),
        'stats': {
            'totalSchedules': len(schedules),
            'activeSchedules': active_count,
            'disabledSchedules': len(schedules) - active_count,
            'totalRecipients': sum(len(schedule.get('recipients', [])) for schedule in schedules),
        },
        'schedules': [_serialize_report_schedule(schedule) for schedule in sorted(schedules, key=lambda item: item.get('updatedAt') or '', reverse=True)],
    }


def _serialize_security_block(block):
    return {
        **block,
        'blockedDate': _format_state_timestamp(block.get('blockedDate')),
    }


def _serialize_security_violation(violation):
    return {
        **violation,
        'timestamp': _format_state_timestamp(violation.get('timestamp')),
    }


def _build_security_payload():
    state = _load_admin_state()
    security_state = state.get('security', {})
    blocked_ips = security_state.get('blockedIps', [])
    violations = security_state.get('violations', [])
    rate_limit = security_state.get('rateLimit', {})
    active_violations = [violation for violation in violations if violation.get('status') == 'active']
    suspicious_patterns = sum(1 for block in blocked_ips if block.get('severity') in {'medium', 'high', 'critical'})
    malware_detections = sum(1 for block in blocked_ips if 'malware' in (block.get('reason') or '').lower())

    return {
        'generatedAt': _admin_now().isoformat(),
        'stats': {
            'blockedIPs': len(blocked_ips),
            'rateLimitViolations': len(active_violations),
            'suspiciousPatterns': suspicious_patterns,
            'malwareDetections': malware_detections,
        },
        'blockedIPs': [_serialize_security_block(block) for block in sorted(blocked_ips, key=lambda item: item.get('blockedDate') or '', reverse=True)],
        'violations': [_serialize_security_violation(violation) for violation in sorted(violations, key=lambda item: item.get('timestamp') or '', reverse=True)],
        'rateLimit': {
            **rate_limit,
            'updatedAt': _format_state_timestamp(rate_limit.get('updatedAt')),
        },
    }


def _find_state_item(items, item_id):
    for item in items:
        if item.get('id') == item_id:
            return item
    return None


def _format_admin_date(value):
    if not value:
        return None
    return value.strftime('%Y-%m-%d')


def _format_admin_datetime(value):
    if not value:
        return None
    return value.strftime('%Y-%m-%d %H:%M')


def _format_admin_datetime_input(value):
    if not value:
        return None
    return value.strftime('%Y-%m-%dT%H:%M')


def _format_bytes_compact(value):
    size = float(value or 0)
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f'{int(size)} {units[unit_index]}'
    return f'{size:.1f} {units[unit_index]}'


def _format_duration_compact(seconds):
    duration = float(seconds or 0)
    if duration <= 0:
        return '0.0s'
    if duration < 60:
        return f'{duration:.1f}s'
    minutes = int(duration // 60)
    remainder = int(duration % 60)
    return f'{minutes}m {remainder}s'


def _serialize_conversion_monitoring_job(conversion, user=None):
    effective_duration = conversion.processing_time
    if effective_duration is None and conversion.status == 'processing':
        reference_time = conversion.started_at or conversion.created_at
        if reference_time:
            effective_duration = max(0.0, (datetime.now(timezone.utc) - reference_time).total_seconds())

    user_label = 'Unknown user'
    if user:
        user_label = user.username or user.email or f'User {user.id}'

    return {
        'id': conversion.id,
        'displayId': f'CVT-{conversion.id:06d}',
        'userId': conversion.user_id,
        'user': user_label,
        'inputFormat': (conversion.input_format or 'unknown').upper(),
        'outputFormat': (conversion.output_format or 'unknown').upper(),
        'fileSizeBytes': conversion.input_size or 0,
        'fileSizeLabel': _format_bytes_compact(conversion.input_size or 0),
        'status': (conversion.status or 'pending').lower(),
        'processingTimeSeconds': round(float(effective_duration or 0), 2),
        'processingTimeLabel': _format_duration_compact(effective_duration or 0),
        'workerNode': conversion.worker_id or 'Unassigned',
        'createdAt': _format_admin_datetime(conversion.created_at),
        'createdAtIso': _format_monitoring_timestamp(conversion.created_at),
        'filename': conversion.input_filename,
        'outputFilename': conversion.output_filename,
        'errorMessage': conversion.error_message,
        'isLarge': (conversion.input_size or 0) > (5 * 1024 * 1024),
        'isSlow': float(effective_duration or 0) > 2,
    }


def _parse_plan_change(description):
    prefix = 'Plan changed from '
    if not description or not description.startswith(prefix) or ' to ' not in description:
        return None, None

    plans = description[len(prefix):].split(' to ', 1)
    if len(plans) != 2:
        return None, None

    return plans[0], plans[1]


def _get_public_billing_provider_endpoint():
    path = '/api/admin/billing/provider-events'
    try:
        return f"{request.url_root.rstrip('/')}{path}"
    except RuntimeError:
        return path


def _parse_pagination(prefix, default_per_page):
    page = request.args.get(f'{prefix}_page', 1, type=int) or 1
    per_page = request.args.get(f'{prefix}_per_page', default_per_page, type=int) or default_per_page
    page = max(1, page)
    per_page = max(1, min(per_page, MAX_BILLING_PAGE_SIZE))
    return page, per_page


def _serialize_pagination(pagination):
    return {
        'total': pagination.total,
        'pages': pagination.pages,
        'currentPage': pagination.page,
        'perPage': pagination.per_page,
        'hasNext': pagination.has_next,
        'hasPrev': pagination.has_prev,
        'nextPage': pagination.next_num if pagination.has_next else None,
        'prevPage': pagination.prev_num if pagination.has_prev else None,
    }


def _status_weight(status):
    return {
        'healthy': 0,
        'idle': 0,
        'active': 0,
        'busy': 1,
        'warning': 1,
        'degraded': 1,
        'not_configured': 1,
        'unknown': 1,
        'offline': 2,
        'error': 2,
        'critical': 2,
        'unhealthy': 2,
    }.get((status or 'unknown').lower(), 1)


def _combine_statuses(statuses):
    normalized = [(status or 'unknown').lower() for status in statuses if status]
    if not normalized:
        return 'unknown'

    highest_weight = max(_status_weight(status) for status in normalized)
    if highest_weight >= 2:
        return 'unhealthy'
    if highest_weight == 1:
        return 'degraded'
    return 'healthy'


def _to_admin_status(status):
    normalized = (status or 'unknown').lower()
    if normalized in {'healthy', 'active', 'idle'}:
        return 'healthy'
    if normalized in {'busy', 'warning', 'degraded', 'not_configured', 'unknown'}:
        return 'warning'
    return 'critical'


def _format_monitoring_timestamp(value):
    if not value:
        return None
    if isinstance(value, str):
        return value
    return value.isoformat()


def _get_uptime_seconds():
    started_at = current_app.config.get('APP_STARTED_AT')
    if not isinstance(started_at, datetime):
        return None
    return max(0, int((datetime.now(timezone.utc) - started_at).total_seconds()))


def _get_database_component_health():
    started = datetime.now(timezone.utc)
    try:
        db.session.execute(text('SELECT 1'))
        response_time_ms = round((datetime.now(timezone.utc) - started).total_seconds() * 1000, 2)
        return {
            'status': 'healthy',
            'message': 'Database connected',
            'responseTimeMs': response_time_ms,
        }
    except Exception as exc:
        return {
            'status': 'unhealthy',
            'message': f'Database error: {str(exc)}',
        }


def _get_cache_component_health():
    try:
        from app.health_check import check_redis_health

        cache_health = check_redis_health()
        return {
            'status': (cache_health.get('status') or 'unknown').lower(),
            'message': cache_health.get('message') or 'Cache probe complete',
        }
    except Exception as exc:
        return {
            'status': 'degraded',
            'message': f'Cache probe failed: {str(exc)}',
        }


def _get_storage_component_health():
    try:
        try:
            import psutil
        except ImportError:
            psutil = None

        if psutil is None:
            return {
                'status': 'unknown',
                'message': 'psutil not installed',
            }

        storage_path = os.path.abspath(current_app.config.get('DATABASE_PATH') or os.getcwd())
        if os.path.isfile(storage_path):
            storage_path = os.path.dirname(storage_path)

        disk = psutil.disk_usage(storage_path)
        status = 'healthy'
        if disk.percent >= 95:
            status = 'unhealthy'
        elif disk.percent >= 85:
            status = 'degraded'

        return {
            'status': status,
            'path': storage_path,
            'diskPercent': round(disk.percent, 2),
            'freeGb': round(disk.free / (1024 ** 3), 2),
        }
    except Exception as exc:
        return {
            'status': 'unknown',
            'message': f'Storage probe failed: {str(exc)}',
        }


def _get_system_metrics_snapshot():
    metrics_collector = current_app.config.get('METRICS_COLLECTOR')
    snapshot = None
    if metrics_collector:
        try:
            snapshot = metrics_collector.collect_metrics()
        except Exception:
            snapshot = None

    try:
        try:
            import psutil
        except ImportError:
            psutil = None

        if psutil is None:
            disk_percent = 0.0
            cpu_usage = round(getattr(snapshot, 'cpu_utilization', 0.0) or 0.0, 2)
            memory_usage = round(getattr(snapshot, 'memory_utilization', 0.0) or 0.0, 2)
        else:
            cpu_usage = round(psutil.cpu_percent(interval=0.1), 2)
            memory_usage = round(psutil.virtual_memory().percent, 2)
            storage_path = os.path.abspath(current_app.config.get('DATABASE_PATH') or os.getcwd())
            if os.path.isfile(storage_path):
                storage_path = os.path.dirname(storage_path)
            disk_percent = round(psutil.disk_usage(storage_path).percent, 2)
    except Exception:
        cpu_usage = round(getattr(snapshot, 'cpu_utilization', 0.0) or 0.0, 2)
        memory_usage = round(getattr(snapshot, 'memory_utilization', 0.0) or 0.0, 2)
        disk_percent = 0.0

    active_users = UserSession.query.filter(
        UserSession.revoked_at.is_(None),
        UserSession.last_active_at >= datetime.now(timezone.utc) - timedelta(minutes=30),
    ).count()

    recent_conversions_query = Conversion.query.filter(
        Conversion.created_at >= datetime.now(timezone.utc) - timedelta(hours=24)
    )
    recent_conversions = recent_conversions_query.count()
    recent_failed_conversions = recent_conversions_query.filter(Conversion.status == 'failed').count()
    error_rate = round((recent_failed_conversions / recent_conversions) * 100, 2) if recent_conversions else 0.0

    return {
        'cpuUsage': cpu_usage,
        'memoryUsage': memory_usage,
        'diskUsage': disk_percent,
        'apiResponseTime': round(getattr(snapshot, 'average_response_time', 0.0) or 0.0, 2),
        'activeUsers': active_users,
        'requestsPerSecond': round(getattr(snapshot, 'request_rate', 0.0) or 0.0, 2),
        'errorRate': error_rate,
        'uptimeSeconds': _get_uptime_seconds() or 0,
    }


def _get_worker_monitoring_payload():
    if not current_app.config.get('ENABLE_BACKGROUND_TASKS', True):
        return {
            'status': 'healthy',
            'message': 'Background workers are disabled in this environment',
            'stats': {
                'activeWorkers': 0,
                'queueSize': 0,
                'avgProcessingTimeMs': 0,
                'workerErrors': 0,
                'memoryUsageMb': 0,
            },
            'workers': [],
        }

    celery_app = getattr(current_app, 'celery', None)
    if not celery_app:
        return {
            'status': 'healthy',
            'message': 'Celery is not configured for this environment',
            'stats': {
                'activeWorkers': 0,
                'queueSize': 0,
                'avgProcessingTimeMs': 0,
                'workerErrors': 0,
                'memoryUsageMb': 0,
            },
            'workers': [],
        }

    broker_url = str(current_app.config.get('CELERY_BROKER_URL') or '')
    result_backend = str(current_app.config.get('CELERY_RESULT_BACKEND') or '')
    using_local_task_mode = broker_url.startswith('memory://') or result_backend.startswith('cache+memory://')

    try:
        inspector = celery_app.control.inspect(timeout=1.0)
        stats_by_worker = inspector.stats() or {}
        active_by_worker = inspector.active() or {}
        reserved_by_worker = inspector.reserved() or {}
        scheduled_by_worker = inspector.scheduled() or {}
        ping_response = inspector.ping() or []
    except Exception as exc:
        return {
            'status': 'healthy' if using_local_task_mode else 'degraded',
            'message': 'Workers are running in local in-memory mode' if using_local_task_mode else f'Failed to inspect workers: {str(exc)}',
            'stats': {
                'activeWorkers': 0,
                'queueSize': 0,
                'avgProcessingTimeMs': 0,
                'workerErrors': 0 if using_local_task_mode else 1,
                'memoryUsageMb': 0,
            },
            'workers': [],
        }

    ping_by_worker = {}
    if isinstance(ping_response, list):
        for item in ping_response:
            if isinstance(item, dict):
                ping_by_worker.update(item)
    elif isinstance(ping_response, dict):
        ping_by_worker = ping_response

    known_workers = set(stats_by_worker) | set(active_by_worker) | set(reserved_by_worker) | set(scheduled_by_worker) | set(ping_by_worker)
    worker_rows = []
    total_queue = 0
    total_memory_mb = 0.0
    offline_workers = 0

    for worker_name in sorted(known_workers):
        worker_stats = stats_by_worker.get(worker_name) or {}
        active_tasks = active_by_worker.get(worker_name) or []
        reserved_tasks = reserved_by_worker.get(worker_name) or []
        scheduled_tasks = scheduled_by_worker.get(worker_name) or []
        queue_depth = len(active_tasks) + len(reserved_tasks) + len(scheduled_tasks)
        total_queue += queue_depth

        is_online = worker_name in ping_by_worker or bool(worker_stats)
        if not is_online:
            status = 'offline'
            offline_workers += 1
        elif queue_depth > 0:
            status = 'busy'
        elif active_tasks:
            status = 'active'
        else:
            status = 'idle'

        rusage = worker_stats.get('rusage') or {}
        maxrss = rusage.get('maxrss')
        memory_mb = round(float(maxrss) / 1024, 2) if isinstance(maxrss, (int, float)) else 0.0
        total_memory_mb += memory_mb
        pool = worker_stats.get('pool') or {}

        worker_rows.append({
            'id': worker_name,
            'name': worker_name.split('@', 1)[0],
            'status': status,
            'queue': queue_depth,
            'avgTimeMs': None,
            'errors': 0 if is_online else 1,
            'memoryMb': memory_mb,
            'lastHeartbeat': _format_monitoring_timestamp(datetime.now(timezone.utc) if is_online else None),
            'poolProcessCount': pool.get('max-concurrency') or pool.get('max_concurrency') or 0,
            'activeTasks': len(active_tasks),
            'reservedTasks': len(reserved_tasks),
            'scheduledTasks': len(scheduled_tasks),
        })

    metrics = _get_system_metrics_snapshot()
    active_workers = sum(1 for worker in worker_rows if worker['status'] != 'offline')

    return {
        'status': _combine_statuses(['healthy' if active_workers else 'degraded', 'unhealthy' if offline_workers else 'healthy']),
        'message': 'Worker status loaded from Celery inspect',
        'stats': {
            'activeWorkers': active_workers,
            'queueSize': total_queue,
            'avgProcessingTimeMs': metrics['apiResponseTime'],
            'workerErrors': offline_workers,
            'memoryUsageMb': round(total_memory_mb, 2),
        },
        'workers': worker_rows,
    }


def _calculate_percent_change(current_value, previous_value):
    current_value = float(current_value or 0)
    previous_value = float(previous_value or 0)
    if previous_value == 0:
        return 0.0 if current_value == 0 else 100.0
    return round(((current_value - previous_value) / previous_value) * 100, 1)


def _get_admin_analytics_overview(days=7):
    days = max(1, min(int(days or 7), 30))
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day)
    metrics = _get_system_metrics_snapshot()
    worker_payload = _get_worker_monitoring_payload()

    last_24_hours = now - timedelta(hours=24)
    previous_24_hours = last_24_hours - timedelta(hours=24)
    success_last_24h = Conversion.query.filter(
        Conversion.created_at >= last_24_hours,
        Conversion.status == 'completed',
    ).count()
    total_last_24h = Conversion.query.filter(Conversion.created_at >= last_24_hours).count()
    success_previous_24h = Conversion.query.filter(
        Conversion.created_at >= previous_24_hours,
        Conversion.created_at < last_24_hours,
        Conversion.status == 'completed',
    ).count()
    total_previous_24h = Conversion.query.filter(
        Conversion.created_at >= previous_24_hours,
        Conversion.created_at < last_24_hours,
    ).count()

    active_subscriptions = Subscription.query.filter(
        Subscription.is_active == True,
        Subscription.plan != 'free',
    ).all()
    monthly_recurring_revenue = round(sum(item.price_per_month or 0 for item in active_subscriptions), 2)

    queue_size = Conversion.query.filter_by(status='pending').count()
    active_users = metrics.get('activeUsers', 0)
    total_users = User.query.count()
    completed_today = Conversion.query.filter(
        Conversion.created_at >= today_start,
        Conversion.status == 'completed',
    ).count()
    failed_today = Conversion.query.filter(
        Conversion.created_at >= today_start,
        Conversion.status == 'failed',
    ).count()

    avg_processing_today = db.session.query(func.avg(Conversion.processing_time)).filter(
        Conversion.created_at >= today_start,
        Conversion.status == 'completed',
        Conversion.processing_time.isnot(None),
    ).scalar() or 0
    avg_processing_previous = db.session.query(func.avg(Conversion.processing_time)).filter(
        Conversion.created_at >= today_start - timedelta(days=1),
        Conversion.created_at < today_start,
        Conversion.status == 'completed',
        Conversion.processing_time.isnot(None),
    ).scalar() or 0

    trend_days = []
    for offset in range(days - 1, -1, -1):
        bucket_start = today_start - timedelta(days=offset)
        bucket_end = bucket_start + timedelta(days=1)
        label = bucket_start.strftime('%a') if days <= 7 else bucket_start.strftime('%m-%d')
        total = Conversion.query.filter(
            Conversion.created_at >= bucket_start,
            Conversion.created_at < bucket_end,
        ).count()
        completed = Conversion.query.filter(
            Conversion.created_at >= bucket_start,
            Conversion.created_at < bucket_end,
            Conversion.status == 'completed',
        ).count()
        trend_days.append({
            'label': label,
            'total': total,
            'completed': completed,
        })

    format_rows = db.session.query(
        Conversion.output_format,
        func.count(Conversion.id).label('count')
    ).filter(
        Conversion.status == 'completed',
        Conversion.created_at >= today_start - timedelta(days=max(days, 7)),
    ).group_by(Conversion.output_format).order_by(
        func.count(Conversion.id).desc()
    ).limit(5).all()

    plan_counts = Counter((plan or 'free').title() for plan, in db.session.query(User.plan).all())
    role_counts = Counter((role or 'user').title() for role, in db.session.query(User.role).all())

    top_formats = [
        {'name': (fmt or 'Unknown').upper(), 'visits': count, 'rate': round((count / max(total_last_24h, 1)) * 100, 1)}
        for fmt, count in format_rows
    ]

    traffic_sources = [
        {'source': 'Active Users', 'visitors': active_users, 'percentage': round((active_users / max(total_users, 1)) * 100, 1)},
        {'source': 'Subscribers', 'visitors': len(active_subscriptions), 'percentage': round((len(active_subscriptions) / max(total_users, 1)) * 100, 1)},
        {'source': 'Queue Demand', 'visitors': queue_size, 'percentage': round((queue_size / max(total_last_24h, 1)) * 100, 1) if total_last_24h else 0.0},
        {'source': 'Worker Capacity', 'visitors': worker_payload.get('stats', {}).get('activeWorkers', 0), 'percentage': round((worker_payload.get('stats', {}).get('activeWorkers', 0) / max(worker_payload.get('stats', {}).get('activeWorkers', 0) + queue_size, 1)) * 100, 1)},
    ]

    alerts = _build_system_alerts(
        metrics,
        {
            'database': _get_database_component_health(),
            'api': {'status': 'healthy', 'message': 'Admin API responding'},
            'cache': _get_cache_component_health(),
            'workers': {'status': worker_payload.get('status'), 'message': worker_payload.get('message')},
            'storage': _get_storage_component_health(),
        },
        worker_payload,
    )

    metrics_rows = [
        {
            'id': 'requests_per_second',
            'name': 'Request Rate',
            'type': 'system',
            'current': round(float(metrics.get('requestsPerSecond', 0)), 2),
            'previous': round(float(success_previous_24h), 2),
            'change': _calculate_percent_change(metrics.get('requestsPerSecond', 0), success_previous_24h),
            'unit': 'req/s',
            'description': 'Current request throughput captured by the autoscaling metrics collector.',
        },
        {
            'id': 'api_response_time',
            'name': 'API Response Time',
            'type': 'service',
            'current': round(float(metrics.get('apiResponseTime', 0)), 2),
            'previous': round(float(avg_processing_previous * 1000), 2),
            'change': _calculate_percent_change(metrics.get('apiResponseTime', 0), avg_processing_previous * 1000),
            'unit': 'ms',
            'description': 'Average API latency from the live system metrics snapshot.',
        },
        {
            'id': 'error_rate',
            'name': 'Error Rate',
            'type': 'system',
            'current': round(float(metrics.get('errorRate', 0)), 2),
            'previous': round((1 - (success_previous_24h / total_previous_24h)) * 100, 2) if total_previous_24h else 0.0,
            'change': _calculate_percent_change(metrics.get('errorRate', 0), round((1 - (success_previous_24h / total_previous_24h)) * 100, 2) if total_previous_24h else 0.0),
            'unit': '%',
            'description': '24-hour conversion failure rate based on recent conversion records.',
        },
        {
            'id': 'active_users',
            'name': 'Active Users',
            'type': 'business',
            'current': active_users,
            'previous': UserSession.query.filter(
                UserSession.revoked_at.is_(None),
                UserSession.last_active_at >= datetime.now(timezone.utc) - timedelta(minutes=60),
                UserSession.last_active_at < datetime.now(timezone.utc) - timedelta(minutes=30),
            ).count(),
            'change': 0.0,
            'unit': 'users',
            'description': 'Sessions active within the last 30 minutes.',
        },
        {
            'id': 'queue_depth',
            'name': 'Queue Depth',
            'type': 'service',
            'current': queue_size,
            'previous': worker_payload.get('stats', {}).get('queueSize', 0),
            'change': _calculate_percent_change(queue_size, worker_payload.get('stats', {}).get('queueSize', 0)),
            'unit': 'jobs',
            'description': 'Pending conversions waiting for worker capacity.',
        },
        {
            'id': 'monthly_recurring_revenue',
            'name': 'Monthly Recurring Revenue',
            'type': 'business',
            'current': monthly_recurring_revenue,
            'previous': 0,
            'change': 0.0,
            'unit': 'USD',
            'description': 'Recurring subscription revenue from active paid plans.',
        },
    ]

    active_users_previous = metrics_rows[3]['previous']
    metrics_rows[3]['change'] = _calculate_percent_change(active_users, active_users_previous)

    summary_cards = [
        {
            '_id': 'total_requests',
            'metric_name': 'Total Conversions (24h)',
            'value': total_last_24h,
            'unit': 'jobs',
            'aggregation_level': 'daily',
            'trend': _calculate_percent_change(total_last_24h, total_previous_24h),
        },
        {
            '_id': 'api_response_time',
            'metric_name': 'API Response Time',
            'value': round(float(metrics.get('apiResponseTime', 0)), 2),
            'unit': 'ms',
            'aggregation_level': 'real-time',
            'trend': _calculate_percent_change(metrics.get('apiResponseTime', 0), avg_processing_previous * 1000),
        },
        {
            '_id': 'error_rate',
            'metric_name': 'Error Rate',
            'value': round(float(metrics.get('errorRate', 0)), 2),
            'unit': '%',
            'aggregation_level': 'daily',
            'trend': metrics_rows[2]['change'],
        },
        {
            '_id': 'active_users',
            'metric_name': 'Active Users',
            'value': active_users,
            'unit': 'users',
            'aggregation_level': 'real-time',
            'trend': metrics_rows[3]['change'],
        },
    ]

    return {
        'generatedAt': _format_monitoring_timestamp(now),
        'metrics': summary_cards,
        'metricRows': metrics_rows,
        'charts': {
            'requestVolume': {
                'labels': [item['label'] for item in trend_days],
                'datasets': [
                    {
                        'label': 'Conversions',
                        'data': [item['total'] for item in trend_days],
                        'borderColor': '#3b82f6',
                        'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                    }
                ],
            },
            'dailyDistribution': {
                'labels': [item['label'] for item in trend_days],
                'datasets': [
                    {
                        'label': 'Completed Conversions',
                        'data': [item['completed'] for item in trend_days],
                        'backgroundColor': '#8b5cf6',
                    }
                ],
            },
        },
        'traffic': {
            'realTimeVisitors': active_users,
            'conversionRate': round((success_last_24h / total_last_24h) * 100, 2) if total_last_24h else 0.0,
            'countries': len(role_counts) + len(plan_counts),
            'topPages': top_formats,
            'topPageVisits': top_formats[0]['visits'] if top_formats else 0,
            'topPageName': top_formats[0]['name'] if top_formats else 'N/A',
            'trafficSource': traffic_sources,
        },
        'alerts': [
            {
                'id': item['id'],
                'name': item['id'].replace('-', ' ').title(),
                'metric': item['message'],
                'threshold': item.get('type', 'warning'),
                'severity': item.get('type', 'warning'),
                'status': 'active',
                'lastTriggered': item['time'].replace('T', ' ')[:19] if item.get('time') else None,
            }
            for item in alerts
        ],
    }


def _scan_directory(path):
    if not path or not os.path.exists(path):
        return {
            'exists': False,
            'bytes': 0,
            'files': 0,
            'updatedAt': None,
        }

    total_bytes = 0
    total_files = 0
    latest_mtime = None

    for root, _, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                stat = os.stat(file_path)
            except OSError:
                continue
            total_bytes += stat.st_size
            total_files += 1
            modified_at = datetime.utcfromtimestamp(stat.st_mtime)
            if latest_mtime is None or modified_at > latest_mtime:
                latest_mtime = modified_at

    return {
        'exists': True,
        'bytes': total_bytes,
        'files': total_files,
        'updatedAt': _format_monitoring_timestamp(latest_mtime),
    }


def _analyze_conversion_paths(field_name):
    total_bytes = 0
    total_files = 0
    stale_records = 0
    cleanup_candidates = 0
    latest_mtime = None
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    conversions = Conversion.query.filter(getattr(Conversion, field_name).isnot(None)).all()
    for conversion in conversions:
        file_path = getattr(conversion, field_name)
        if not file_path:
            continue
        if not os.path.exists(file_path):
            stale_records += 1
            continue

        try:
            stat = os.stat(file_path)
        except OSError:
            stale_records += 1
            continue

        total_bytes += stat.st_size
        total_files += 1
        modified_at = datetime.utcfromtimestamp(stat.st_mtime)
        if latest_mtime is None or modified_at > latest_mtime:
            latest_mtime = modified_at

        if (conversion.created_at or datetime.now(timezone.utc)) < cutoff and conversion.status in {'completed', 'failed', 'cancelled'}:
            cleanup_candidates += 1

    return {
        'bytes': total_bytes,
        'files': total_files,
        'staleRecords': stale_records,
        'cleanupCandidates': cleanup_candidates,
        'updatedAt': _format_monitoring_timestamp(latest_mtime),
    }


def _purge_upload_chunks(older_than_seconds=None):
    retention = int(older_than_seconds or current_app.config.get('UPLOAD_CLEANUP_RETENTION', 24 * 3600))
    now_ts = __import__('time').time()
    removed = 0
    base_dir = current_app.config.get('UPLOAD_CHUNKS_DIR')

    if not base_dir or not os.path.exists(base_dir):
        return {
            'removed': 0,
            'baseDir': base_dir,
            'retentionSeconds': retention,
        }

    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        try:
            mtime = os.path.getmtime(path)
            if now_ts - mtime > retention:
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
                removed += 1
        except OSError:
            continue

    return {
        'removed': removed,
        'baseDir': base_dir,
        'retentionSeconds': retention,
    }


def _count_stale_upload_chunks(older_than_seconds=None):
    retention = int(older_than_seconds or current_app.config.get('UPLOAD_CLEANUP_RETENTION', 24 * 3600))
    base_dir = current_app.config.get('UPLOAD_CHUNKS_DIR')
    if not base_dir or not os.path.exists(base_dir):
        return 0

    now_ts = __import__('time').time()
    stale_count = 0
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        try:
            if now_ts - os.path.getmtime(path) > retention:
                stale_count += 1
        except OSError:
            continue
    return stale_count


def _clear_stale_conversion_references():
    cleared_input_paths = 0
    cleared_output_paths = 0

    conversions = Conversion.query.filter(
        Conversion.input_path.isnot(None) | Conversion.output_path.isnot(None)
    ).all()

    for conversion in conversions:
        if conversion.input_path and not os.path.exists(conversion.input_path):
            conversion.input_path = None
            cleared_input_paths += 1
        if conversion.output_path and not os.path.exists(conversion.output_path):
            conversion.output_path = None
            cleared_output_paths += 1

    if cleared_input_paths or cleared_output_paths:
        db.session.commit()

    return {
        'clearedInputPaths': cleared_input_paths,
        'clearedOutputPaths': cleared_output_paths,
        'totalCleared': cleared_input_paths + cleared_output_paths,
    }


def _get_storage_management_payload():
    upload_chunks_dir = current_app.config.get('UPLOAD_CHUNKS_DIR')
    log_dir = current_app.config.get('LOG_DIR')
    database_path = current_app.config.get('DATABASE_PATH')

    upload_scan = _scan_directory(upload_chunks_dir)
    log_scan = _scan_directory(log_dir)
    input_scan = _analyze_conversion_paths('input_path')
    output_scan = _analyze_conversion_paths('output_path')

    total_bytes = upload_scan['bytes'] + log_scan['bytes'] + input_scan['bytes'] + output_scan['bytes']
    total_files = upload_scan['files'] + log_scan['files'] + input_scan['files'] + output_scan['files']
    avg_size = round(total_bytes / total_files, 2) if total_files else 0
    retention_seconds = int(current_app.config.get('UPLOAD_CLEANUP_RETENTION', 24 * 3600))
    interval_seconds = int(current_app.config.get('UPLOAD_CLEANUP_INTERVAL', 3600))

    buckets = [
        {
            'id': 'UPLOAD-STAGING',
            'name': 'Upload Staging',
            'path': upload_chunks_dir,
            'usedBytes': upload_scan['bytes'],
            'usedLabel': _format_bytes_compact(upload_scan['bytes']),
            'files': upload_scan['files'],
            'orphaned': 0,
            'cleanupCandidates': _count_stale_upload_chunks(retention_seconds),
            'lastUpdated': upload_scan['updatedAt'],
            'status': 'healthy' if upload_scan['exists'] else 'warning',
        },
        {
            'id': 'CONVERSION-INPUTS',
            'name': 'Conversion Inputs',
            'path': database_path,
            'usedBytes': input_scan['bytes'],
            'usedLabel': _format_bytes_compact(input_scan['bytes']),
            'files': input_scan['files'],
            'orphaned': input_scan['staleRecords'],
            'cleanupCandidates': input_scan['cleanupCandidates'],
            'lastUpdated': input_scan['updatedAt'],
            'status': 'warning' if input_scan['staleRecords'] else 'healthy',
        },
        {
            'id': 'CONVERSION-OUTPUTS',
            'name': 'Conversion Outputs',
            'path': database_path,
            'usedBytes': output_scan['bytes'],
            'usedLabel': _format_bytes_compact(output_scan['bytes']),
            'files': output_scan['files'],
            'orphaned': output_scan['staleRecords'],
            'cleanupCandidates': output_scan['cleanupCandidates'],
            'lastUpdated': output_scan['updatedAt'],
            'status': 'warning' if output_scan['staleRecords'] else 'healthy',
        },
        {
            'id': 'APPLICATION-LOGS',
            'name': 'Application Logs',
            'path': log_dir,
            'usedBytes': log_scan['bytes'],
            'usedLabel': _format_bytes_compact(log_scan['bytes']),
            'files': log_scan['files'],
            'orphaned': 0,
            'cleanupCandidates': 0,
            'lastUpdated': log_scan['updatedAt'],
            'status': 'healthy' if log_scan['exists'] else 'warning',
        },
    ]

    return {
        'generatedAt': _format_monitoring_timestamp(datetime.now(timezone.utc)),
        'stats': {
            'totalStorageUsed': _format_bytes_compact(total_bytes),
            'totalStorageUsedBytes': total_bytes,
            'tempFileCount': upload_scan['files'],
            'avgFileSize': _format_bytes_compact(avg_size),
            'cleanupSchedule': f'Every {max(1, interval_seconds // 3600)}h • retain {max(1, retention_seconds // 3600)}h',
        },
        'buckets': buckets,
    }


def _get_api_monitoring_payload():
    metrics = _get_system_metrics_snapshot()
    worker_payload = _get_worker_monitoring_payload()
    storage_payload = _get_storage_management_payload()
    components = {
        'database': _get_database_component_health(),
        'cache': _get_cache_component_health(),
        'storage': _get_storage_component_health(),
        'workers': {
            'status': worker_payload.get('status'),
            'message': worker_payload.get('message'),
        },
        'api': {
            'status': 'healthy',
            'message': 'Admin API responding',
        },
    }

    last_24_hours = datetime.now(timezone.utc) - timedelta(hours=24)
    previous_24_hours = last_24_hours - timedelta(hours=24)
    total_last_24h = Conversion.query.filter(Conversion.created_at >= last_24_hours).count()
    completed_last_24h = Conversion.query.filter(
        Conversion.created_at >= last_24_hours,
        Conversion.status == 'completed',
    ).count()
    failed_last_24h = Conversion.query.filter(
        Conversion.created_at >= last_24_hours,
        Conversion.status == 'failed',
    ).count()
    avg_processing_time = db.session.query(func.avg(Conversion.processing_time)).filter(
        Conversion.created_at >= last_24_hours,
        Conversion.status == 'completed',
        Conversion.processing_time.isnot(None),
    ).scalar() or 0

    new_users = User.query.filter(User.created_at >= last_24_hours).count()
    eligible_users = User.query.filter(User.created_at <= datetime.now(timezone.utc) - timedelta(days=30)).count()
    retained_users = User.query.filter(
        User.created_at <= datetime.now(timezone.utc) - timedelta(days=30),
        User.last_login.isnot(None),
        User.last_login >= datetime.now(timezone.utc) - timedelta(days=30),
    ).count()
    retention_rate = round((retained_users / eligible_users) * 100, 2) if eligible_users else 0.0

    active_api_keys = [key for key in APIKey.query.order_by(APIKey.usage_count.desc(), APIKey.created_at.desc()).limit(10).all()]
    api_key_rows = []
    for key in active_api_keys:
        subscription = Subscription.query.filter_by(user_id=key.user_id, is_active=True).order_by(Subscription.created_at.desc()).first()
        plan = (subscription.plan if subscription else 'free') or 'free'
        status = 'expired' if key.is_expired() else ('inactive' if not key.is_active else 'active')
        api_key_rows.append({
            'id': key.id,
            'name': key.name,
            'keyPreview': key.key_preview,
            'usageCount': key.usage_count or 0,
            'lastUsedAt': _format_monitoring_timestamp(key.last_used_at),
            'plan': plan.title(),
            'status': status,
            'scopes': key.scopes or [],
        })

    try:
        from app.rate_limiter import RateLimitConfig

        rate_limit_policies = [
            {
                'plan': plan.title(),
                'requestsPerMinute': limits.get('requests_per_minute'),
                'requestsPerHour': limits.get('requests_per_hour'),
                'requestsPerDay': limits.get('requests_per_day') or 'Unlimited',
                'concurrentConversions': limits.get('concurrent_conversions'),
            }
            for plan, limits in RateLimitConfig.TIERS.items()
        ]
    except Exception:
        rate_limit_policies = []

    endpoint_rows = [
        {
            'endpoint': '/api/admin/health',
            'requests': round(float(metrics.get('requestsPerSecond', 0)) * 60, 2),
            'avgTime': round(float(metrics.get('apiResponseTime', 0)), 2),
            'errors': 0,
            'status': components['api']['status'],
            'detail': components['api']['message'],
        },
        {
            'endpoint': '/api/admin/workers',
            'requests': worker_payload.get('stats', {}).get('activeWorkers', 0),
            'avgTime': round(float(metrics.get('apiResponseTime', 0)), 2),
            'errors': worker_payload.get('stats', {}).get('workerErrors', 0),
            'status': worker_payload.get('status'),
            'detail': worker_payload.get('message'),
        },
        {
            'endpoint': '/api/admin/conversions/monitoring',
            'requests': total_last_24h,
            'avgTime': round(float(avg_processing_time) * 1000, 2),
            'errors': failed_last_24h,
            'status': 'healthy' if failed_last_24h == 0 else ('warning' if failed_last_24h < completed_last_24h else 'critical'),
            'detail': f'{completed_last_24h} completed in the last 24h',
        },
        {
            'endpoint': '/api/admin/storage/overview',
            'requests': storage_payload['stats']['tempFileCount'],
            'avgTime': round(float(metrics.get('apiResponseTime', 0)), 2),
            'errors': sum(item['orphaned'] for item in storage_payload['buckets']),
            'status': 'warning' if sum(item['orphaned'] for item in storage_payload['buckets']) else 'healthy',
            'detail': storage_payload['stats']['totalStorageUsed'],
        },
    ]

    return {
        'generatedAt': _format_monitoring_timestamp(datetime.now(timezone.utc)),
        'conversionMetrics': {
            'successRate': round((completed_last_24h / total_last_24h) * 100, 2) if total_last_24h else 0.0,
            'avgProcessingTime': round(float(avg_processing_time), 2),
            'queueDepth': worker_payload.get('stats', {}).get('queueSize', 0),
        },
        'userMetrics': {
            'newUsersPerDay': new_users,
            'activeUsers': metrics.get('activeUsers', 0),
            'retention': retention_rate,
        },
        'infraMetrics': {
            'cpuUsage': metrics.get('cpuUsage', 0),
            'memoryUsage': metrics.get('memoryUsage', 0),
            'diskUsage': metrics.get('diskUsage', 0),
        },
        'stats': {
            'requestRate': metrics.get('requestsPerSecond', 0),
            'avgResponseTime': metrics.get('apiResponseTime', 0),
            'errorRate': metrics.get('errorRate', 0),
            'activeApiKeys': sum(1 for key in api_key_rows if key['status'] == 'active'),
            'totalApiKeys': APIKey.query.count(),
        },
        'endpoints': endpoint_rows,
        'apiKeys': api_key_rows,
        'rateLimitPolicies': rate_limit_policies,
    }


def _plan_code_to_label(plan_code):
    plan_map = {
        'free': 'Basic',
        'pro': 'Professional',
        'enterprise': 'Enterprise',
    }
    return plan_map.get((plan_code or 'free').lower(), (plan_code or 'free').title())


def _user_role_to_department(role):
    department_map = {
        'admin': 'Management',
        'moderator': 'Operations',
        'user': 'Support',
    }
    return department_map.get((role or 'user').lower(), 'Operations')


def _generate_temporary_password(length=14):
    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _get_user_last_activity_at(user):
    candidates = []

    if user.last_login:
        candidates.append(user.last_login)

    recent_session = user.sessions.order_by(UserSession.last_active_at.desc()).first()
    if recent_session and recent_session.last_active_at:
        candidates.append(recent_session.last_active_at)

    recent_conversion = user.conversions.order_by(Conversion.created_at.desc()).first()
    if recent_conversion and recent_conversion.created_at:
        candidates.append(recent_conversion.created_at)

    return max(candidates) if candidates else None


def _serialize_admin_user_list_item(user):
    last_activity_at = _get_user_last_activity_at(user)
    conversions_count = user.conversions.count()
    display_name = ' '.join(part for part in [user.first_name, user.last_name] if part).strip() or user.username or user.email

    return {
        **user.to_dict(),
        'displayId': f'USR-{user.id:06d}',
        'name': display_name,
        'signupDate': _format_admin_date(user.created_at),
        'planLabel': _plan_code_to_label(user.plan),
        'status': 'active' if user.is_active else 'suspended',
        'conversionsCount': conversions_count,
        'lastActivity': _format_admin_datetime(last_activity_at),
        'lastActivityIso': _format_monitoring_timestamp(last_activity_at),
        'department': _user_role_to_department(user.role),
    }


def _append_activity_event(events, event):
    timestamp = event.get('timestamp')
    if not timestamp:
        return
    events.append(event)


def _build_admin_activity_events(period_days=30, limit=200):
    cutoff = datetime.now(timezone.utc) - timedelta(days=max(1, min(period_days, 365)))
    events = []

    recent_users = User.query.filter(
        or_(User.created_at >= cutoff, User.last_login >= cutoff, User.updated_at >= cutoff)
    ).all()
    for user in recent_users:
        display_name = ' '.join(part for part in [user.first_name, user.last_name] if part).strip() or user.username or user.email

        if user.created_at and user.created_at >= cutoff:
            _append_activity_event(events, {
                'id': f'user-created-{user.id}',
                'timestamp': user.created_at.isoformat(),
                'action': 'user-created',
                'userId': str(user.id),
                'userName': display_name,
                'resourceType': 'user',
                'resourceId': str(user.id),
                'resourceName': user.email,
                'status': 'success',
                'severity': 'info',
                'details': {
                    'plan': user.plan,
                    'role': user.role,
                },
                'source': 'users',
            })

        if user.last_login and user.last_login >= cutoff:
            _append_activity_event(events, {
                'id': f'user-login-{user.id}-{user.last_login.isoformat()}',
                'timestamp': user.last_login.isoformat(),
                'action': 'user-login',
                'userId': str(user.id),
                'userName': display_name,
                'resourceType': 'auth',
                'resourceId': str(user.id),
                'resourceName': user.email,
                'status': 'success',
                'severity': 'info',
                'details': {
                    'role': user.role,
                },
                'source': 'auth',
            })

        if user.updated_at and user.created_at and user.updated_at >= cutoff and (user.updated_at - user.created_at) > timedelta(minutes=5):
            _append_activity_event(events, {
                'id': f'user-updated-{user.id}-{user.updated_at.isoformat()}',
                'timestamp': user.updated_at.isoformat(),
                'action': 'user-updated',
                'userId': str(user.id),
                'userName': display_name,
                'resourceType': 'user',
                'resourceId': str(user.id),
                'resourceName': user.email,
                'status': 'success',
                'severity': 'warning',
                'details': {
                    'isActive': user.is_active,
                    'plan': user.plan,
                    'role': user.role,
                },
                'source': 'users',
            })

    recent_conversions = Conversion.query.filter(
        or_(Conversion.created_at >= cutoff, Conversion.completed_at >= cutoff)
    ).order_by(Conversion.created_at.desc()).limit(limit * 2).all()
    for conversion in recent_conversions:
        event_time = conversion.completed_at or conversion.created_at
        if not event_time or event_time < cutoff:
            continue

        user = conversion.user
        _append_activity_event(events, {
            'id': f'conversion-{conversion.id}-{conversion.status}',
            'timestamp': event_time.isoformat(),
            'action': f'conversion-{conversion.status}',
            'userId': str(conversion.user_id),
            'userName': (user.username if user else None) or (user.email if user else None) or f'User {conversion.user_id}',
            'resourceType': 'conversion',
            'resourceId': str(conversion.id),
            'resourceName': conversion.input_filename,
            'status': 'success' if conversion.status == 'completed' else ('error' if conversion.status == 'failed' else conversion.status),
            'severity': 'critical' if conversion.status == 'failed' else ('warning' if conversion.status in {'cancelled', 'processing'} else 'info'),
            'details': {
                'inputFormat': conversion.input_format,
                'outputFormat': conversion.output_format,
                'processingTime': conversion.processing_time,
                'workerId': conversion.worker_id,
                'errorMessage': conversion.error_message,
            },
            'source': 'conversions',
        })

    recent_billing_events = BillingAuditLog.query.filter(
        BillingAuditLog.created_at >= cutoff
    ).order_by(BillingAuditLog.created_at.desc()).limit(limit).all()
    for entry in recent_billing_events:
        _append_activity_event(events, {
            'id': f'billing-audit-{entry.id}',
            'timestamp': entry.created_at.isoformat(),
            'action': entry.action or 'billing-status-change',
            'userId': str(entry.user_id) if entry.user_id is not None else '',
            'userName': entry.actor_username or entry.actor_email or 'system',
            'resourceType': 'billing',
            'resourceId': str(entry.invoice_id),
            'resourceName': entry.invoice.invoice_number if entry.invoice else None,
            'status': entry.to_status or 'success',
            'severity': 'warning' if entry.to_status in {'failed', 'refunded'} else 'info',
            'details': {
                'fromStatus': entry.from_status,
                'toStatus': entry.to_status,
                'statusNote': entry.status_note,
            },
            'source': 'billing',
        })

    recent_api_keys = APIKey.query.filter(
        or_(APIKey.created_at >= cutoff, APIKey.last_used_at >= cutoff)
    ).order_by(APIKey.created_at.desc()).limit(limit).all()
    for key in recent_api_keys:
        if key.created_at and key.created_at >= cutoff:
            _append_activity_event(events, {
                'id': f'api-key-created-{key.id}',
                'timestamp': key.created_at.isoformat(),
                'action': 'api-key-created',
                'userId': str(key.user_id),
                'userName': key.user.username if key.user else f'User {key.user_id}',
                'resourceType': 'api_key',
                'resourceId': str(key.id),
                'resourceName': key.name,
                'status': 'success',
                'severity': 'info',
                'details': {
                    'keyPreview': key.key_preview,
                    'scopes': key.scopes,
                },
                'source': 'api_keys',
            })

        if key.last_used_at and key.last_used_at >= cutoff:
            _append_activity_event(events, {
                'id': f'api-key-used-{key.id}-{key.last_used_at.isoformat()}',
                'timestamp': key.last_used_at.isoformat(),
                'action': 'api-key-used',
                'userId': str(key.user_id),
                'userName': key.user.username if key.user else f'User {key.user_id}',
                'resourceType': 'api_key',
                'resourceId': str(key.id),
                'resourceName': key.name,
                'status': 'success',
                'severity': 'info',
                'details': {
                    'usageCount': key.usage_count,
                    'keyPreview': key.key_preview,
                },
                'source': 'api_keys',
            })

    state = _load_admin_state()
    for event in state.get('activityEvents', []):
        event_time = _parse_state_timestamp(event.get('timestamp'))
        if not event_time or event_time < cutoff:
            continue
        _append_activity_event(events, event)

    events.sort(key=lambda item: item['timestamp'], reverse=True)
    return events[:limit]


def _filter_admin_activity_events(events, filters):
    filtered = list(events)

    if filters.get('userId'):
        user_id_filter = filters['userId'].lower()
        filtered = [event for event in filtered if user_id_filter in (event.get('userId') or '').lower() or user_id_filter in (event.get('userName') or '').lower()]
    if filters.get('action'):
        filtered = [event for event in filtered if event.get('action') == filters['action']]
    if filters.get('severity'):
        filtered = [event for event in filtered if event.get('severity') == filters['severity']]
    if filters.get('status'):
        filtered = [event for event in filtered if (event.get('status') or '').lower() == filters['status'].lower()]
    if filters.get('startDate'):
        filtered = [event for event in filtered if event.get('timestamp') and event['timestamp'] >= filters['startDate']]
    if filters.get('endDate'):
        filtered = [event for event in filtered if event.get('timestamp') and event['timestamp'] <= filters['endDate']]

    return filtered


def _build_activity_stats(events):
    today = datetime.now(timezone.utc).date()
    by_severity = Counter((event.get('severity') or 'info') for event in events)
    by_action = Counter((event.get('action') or 'unknown') for event in events)
    return {
        'totalEvents': len(events),
        'today': sum(1 for event in events if event.get('timestamp') and datetime.fromisoformat(event['timestamp']).date() == today),
        'critical': by_severity.get('critical', 0),
        'warnings': by_severity.get('warning', 0),
        'bySeverity': dict(by_severity),
        'byAction': dict(by_action),
    }


def _build_system_alerts(metrics, components, worker_payload):
    alerts = []
    now = datetime.now(timezone.utc).isoformat()

    for component_name, component in components.items():
        component_status = (component.get('status') or 'unknown').lower()
        if component_status in {'degraded', 'unhealthy', 'offline'}:
            alerts.append({
                'id': f'{component_name}-{component_status}',
                'type': 'error' if component_status in {'unhealthy', 'offline'} else 'warning',
                'message': component.get('message') or f'{component_name.title()} is {component_status}',
                'time': now,
            })

    if metrics['memoryUsage'] >= 80:
        alerts.append({
            'id': 'memory-usage',
            'type': 'warning',
            'message': f"Memory usage is elevated at {metrics['memoryUsage']}%",
            'time': now,
        })
    if worker_payload['stats']['queueSize'] >= 25:
        alerts.append({
            'id': 'worker-queue',
            'type': 'warning',
            'message': f"Worker queue depth is {worker_payload['stats']['queueSize']} tasks",
            'time': now,
        })
    if metrics['errorRate'] >= 5:
        alerts.append({
            'id': 'error-rate',
            'type': 'error',
            'message': f"Conversion error rate reached {metrics['errorRate']}% over the last 24 hours",
            'time': now,
        })

    return alerts[:10]


def _serialize_admin_invoice(invoice):
    user = invoice.user
    return {
        'id': invoice.id,
        'invoiceNumber': invoice.invoice_number,
        'description': invoice.description,
        'plan': invoice.plan_code.title(),
        'amount': round(invoice.amount or 0.0, 2),
        'currency': invoice.currency or 'USD',
        'status': invoice.status,
        'statusNote': invoice.status_note,
        'refundAmount': round(invoice.refund_amount, 2) if invoice.refund_amount is not None else None,
        'failureCode': invoice.failure_code,
        'failureReason': invoice.failure_reason,
        'gatewayReferenceId': invoice.gateway_reference_id,
        'processorEventAt': _format_admin_datetime_input(invoice.processor_event_at),
        'issuedAt': _format_admin_date(invoice.issued_at),
        'periodStart': _format_admin_date(invoice.period_start),
        'periodEnd': _format_admin_date(invoice.period_end),
        'refundedAt': _format_admin_date(invoice.refunded_at),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
    }


def _parse_refund_amount(raw_value, invoice_amount):
    if raw_value in (None, ''):
        return round(invoice_amount or 0.0, 2)

    try:
        refund_amount = round(float(raw_value), 2)
    except (TypeError, ValueError) as exc:
        raise ValueError('Refund amount must be numeric') from exc

    if refund_amount < 0:
        raise ValueError('Refund amount must be zero or greater')
    if refund_amount > round(invoice_amount or 0.0, 2):
        raise ValueError('Refund amount cannot exceed the invoice amount')

    return refund_amount


def _parse_processor_event_at(raw_value):
    if raw_value in (None, ''):
        return None

    normalized = str(raw_value).strip().replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError('Processor event time must be a valid ISO datetime') from exc


def _apply_invoice_status(invoice, payload):
    normalized_status = (payload.get('status') or '').strip().lower()
    if normalized_status not in BillingInvoice.ALLOWED_STATUSES:
        raise ValueError('Unsupported invoice status')

    gateway_reference_id = (payload.get('gateway_reference_id') or '').strip() or None
    processor_event_at = _parse_processor_event_at(payload.get('processor_event_at'))

    invoice.status = normalized_status
    invoice.status_note = (payload.get('status_note') or '').strip() or None

    if normalized_status == BillingInvoice.STATUS_PAID:
        invoice.paid_at = invoice.paid_at or datetime.now(timezone.utc)
        invoice.refunded_at = None
        invoice.refund_amount = None
        invoice.failure_code = None
        invoice.failure_reason = None
        invoice.gateway_reference_id = gateway_reference_id
        invoice.processor_event_at = processor_event_at
    elif normalized_status == BillingInvoice.STATUS_REFUNDED:
        invoice.refunded_at = datetime.now(timezone.utc)
        invoice.refund_amount = _parse_refund_amount(payload.get('refund_amount'), invoice.amount)
        invoice.failure_code = None
        invoice.failure_reason = None
        invoice.gateway_reference_id = gateway_reference_id
        invoice.processor_event_at = processor_event_at
    else:
        if normalized_status == BillingInvoice.STATUS_FAILED:
            invoice.paid_at = None
            invoice.refunded_at = None
            invoice.refund_amount = None
            invoice.failure_code = (payload.get('failure_code') or '').strip() or None
            invoice.failure_reason = (payload.get('failure_reason') or '').strip() or None
            invoice.gateway_reference_id = gateway_reference_id
            invoice.processor_event_at = processor_event_at
        if normalized_status == BillingInvoice.STATUS_PENDING:
            invoice.paid_at = None
            invoice.refunded_at = None
            invoice.refund_amount = None
            invoice.failure_code = None
            invoice.failure_reason = None
            invoice.gateway_reference_id = None
            invoice.processor_event_at = None

    return invoice


def _record_billing_audit(invoice, actor, from_status, to_status, status_note=None):
    entry = BillingAuditLog(
        invoice_id=invoice.id,
        user_id=invoice.user_id,
        actor_user_id=actor.id,
        actor_username=actor.username,
        actor_email=actor.email,
        action='invoice_status_updated',
        from_status=from_status,
        to_status=to_status,
        status_note=(status_note or '').strip() or None,
    )
    db.session.add(entry)
    return entry


def _record_billing_system_audit(invoice, from_status, to_status, status_note=None, action='provider_event_ingested'):
    entry = BillingAuditLog(
        invoice_id=invoice.id,
        user_id=invoice.user_id,
        actor_user_id=invoice.user_id,
        actor_username='billing-provider',
        actor_email='billing-provider@system.local',
        action=action,
        from_status=from_status,
        to_status=to_status,
        status_note=(status_note or '').strip() or None,
    )
    db.session.add(entry)
    return entry


def _serialize_plan_change(invoice):
    from_plan, to_plan = _parse_plan_change(invoice.description)
    if not from_plan or not to_plan:
        return None

    user = invoice.user
    return {
        'id': invoice.id,
        'invoiceNumber': invoice.invoice_number,
        'changedAt': _format_admin_date(invoice.issued_at),
        'fromPlan': from_plan,
        'toPlan': to_plan,
        'amount': round(invoice.amount or 0.0, 2),
        'currency': invoice.currency or 'USD',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
    }


def _serialize_billing_audit_log(entry):
    return {
        'id': entry.id,
        'invoiceId': entry.invoice_id,
        'userId': entry.user_id,
        'invoiceNumber': entry.invoice.invoice_number if entry.invoice else None,
        'actor': {
            'id': entry.actor_user_id,
            'username': entry.actor_username,
            'email': entry.actor_email,
        },
        'action': entry.action,
        'fromStatus': entry.from_status,
        'toStatus': entry.to_status,
        'statusNote': entry.status_note,
        'createdAt': _format_admin_datetime(entry.created_at),
    }


def _parse_iso_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        return None


def _resolve_provider_invoice(payload):
    invoice_id = payload.get('invoice_id')
    invoice_number = (payload.get('invoice_number') or '').strip()
    gateway_reference_id = (payload.get('gateway_reference_id') or '').strip()

    if invoice_id is not None:
        return BillingInvoice.query.filter_by(id=invoice_id).first()
    if invoice_number:
        return BillingInvoice.query.filter_by(invoice_number=invoice_number).first()
    if gateway_reference_id:
        return BillingInvoice.query.filter_by(gateway_reference_id=gateway_reference_id).first()
    return None


def _format_provider_timestamp(value):
    if value in (None, ''):
        return None

    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value).replace(second=0, microsecond=0).isoformat()

    normalized = str(value).strip()
    return normalized or None


def _amount_from_minor_units(value):
    if value in (None, ''):
        return None

    try:
        return round(float(value) / 100.0, 2)
    except (TypeError, ValueError):
        return None


def _coerce_provider_status(value):
    normalized = (str(value).strip().lower() if value not in (None, '') else '')
    if not normalized:
        return None

    status_map = {
        'paid': BillingInvoice.STATUS_PAID,
        'succeeded': BillingInvoice.STATUS_PAID,
        'success': BillingInvoice.STATUS_PAID,
        'pending': BillingInvoice.STATUS_PENDING,
        'processing': BillingInvoice.STATUS_PENDING,
        'open': BillingInvoice.STATUS_PENDING,
        'failed': BillingInvoice.STATUS_FAILED,
        'uncollectible': BillingInvoice.STATUS_FAILED,
        'declined': BillingInvoice.STATUS_FAILED,
        'refunded': BillingInvoice.STATUS_REFUNDED,
    }

    if normalized in BillingInvoice.ALLOWED_STATUSES:
        return normalized

    return status_map.get(normalized)


def _extract_stripe_reference(stripe_object):
    for key in ('charge', 'payment_intent', 'refund', 'id'):
        raw_value = stripe_object.get(key)
        if isinstance(raw_value, str) and raw_value.strip():
            return raw_value.strip()
    return None


def _normalize_stripe_event_payload(payload):
    stripe_object = payload.get('data', {}).get('object') or {}
    if not isinstance(stripe_object, dict):
        stripe_object = {}

    metadata = stripe_object.get('metadata') or {}
    if not isinstance(metadata, dict):
        metadata = {}

    last_payment_error = stripe_object.get('last_payment_error') or {}
    if not isinstance(last_payment_error, dict):
        last_payment_error = {}

    event_type = (payload.get('type') or '').strip()
    gateway_reference_id = _extract_stripe_reference(stripe_object)
    failure_reason = (
        last_payment_error.get('message')
        or stripe_object.get('failure_message')
        or stripe_object.get('cancellation_reason')
        or payload.get('status_note')
    )
    failure_code = (
        last_payment_error.get('code')
        or stripe_object.get('failure_code')
        or stripe_object.get('status')
    )
    refund_amount = _amount_from_minor_units(
        stripe_object.get('amount_refunded')
        or stripe_object.get('amount')
    )

    return {
        'provider': 'stripe',
        'provider_event_id': (payload.get('id') or '').strip() or None,
        'event_type': event_type,
        'status': _coerce_provider_status(payload.get('status')),
        'status_note': payload.get('status_note') or f'Stripe event {event_type}',
        'invoice_id': metadata.get('docpro_invoice_id') or metadata.get('invoice_id'),
        'invoice_number': metadata.get('docpro_invoice_number') or metadata.get('invoice_number') or stripe_object.get('number'),
        'gateway_reference_id': payload.get('gateway_reference_id') or gateway_reference_id,
        'processor_event_at': payload.get('processor_event_at') or _format_provider_timestamp(payload.get('created') or stripe_object.get('created') or payload.get('created_at')),
        'failure_code': payload.get('failure_code') or failure_code,
        'failure_reason': payload.get('failure_reason') or failure_reason,
        'refund_amount': payload.get('refund_amount') or refund_amount,
    }


def _normalize_provider_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError('Provider event payload must be a JSON object')

    provider = (payload.get('provider') or '').strip().lower()
    if provider == 'stripe':
        return _normalize_stripe_event_payload(payload)

    if payload.get('type') and isinstance(payload.get('data'), dict):
        return _normalize_stripe_event_payload(payload)

    normalized_payload = dict(payload)
    normalized_payload['provider'] = provider or 'generic'
    return normalized_payload


def _infer_provider_status(event_type, explicit_status=None):
    normalized_status = (explicit_status or '').strip().lower()
    if normalized_status:
        if normalized_status not in BillingInvoice.ALLOWED_STATUSES:
            raise ValueError('Provider event status must be one of paid, pending, failed, or refunded')
        return normalized_status

    normalized_event = (event_type or '').strip().lower()
    status_map = {
        'invoice.paid': BillingInvoice.STATUS_PAID,
        'payment.succeeded': BillingInvoice.STATUS_PAID,
        'charge.succeeded': BillingInvoice.STATUS_PAID,
        'invoice.pending': BillingInvoice.STATUS_PENDING,
        'payment.pending': BillingInvoice.STATUS_PENDING,
        'invoice.payment_failed': BillingInvoice.STATUS_FAILED,
        'payment.failed': BillingInvoice.STATUS_FAILED,
        'charge.failed': BillingInvoice.STATUS_FAILED,
        'charge.refunded': BillingInvoice.STATUS_REFUNDED,
        'refund.succeeded': BillingInvoice.STATUS_REFUNDED,
    }
    inferred_status = status_map.get(normalized_event)
    if not inferred_status:
        raise ValueError('Unable to infer invoice status from provider event type')
    return inferred_status


def _verify_provider_event_signature(raw_body):
    secret = current_app.config.get('BILLING_PROVIDER_WEBHOOK_SECRET')
    if not secret:
        return False, 'Billing provider webhook secret is not configured'

    signature = (request.headers.get('X-DocPro-Billing-Signature') or '').strip()
    if not signature:
        return False, 'Missing X-DocPro-Billing-Signature header'

    expected_signature = hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return False, 'Invalid billing provider signature'

    return True, None


def _build_provider_status_payload(payload):
    event_type = (payload.get('event_type') or '').strip()
    event_status = _infer_provider_status(event_type, payload.get('status'))
    provider_note = (payload.get('status_note') or payload.get('failure_reason') or event_type or 'Provider event sync').strip()
    return {
        'status': event_status,
        'status_note': provider_note,
        'failure_code': payload.get('failure_code'),
        'failure_reason': payload.get('failure_reason'),
        'refund_amount': payload.get('refund_amount'),
        'gateway_reference_id': payload.get('gateway_reference_id'),
        'processor_event_at': payload.get('processor_event_at') or payload.get('occurred_at'),
    }


def _invoice_state_snapshot(invoice):
    return (
        invoice.status,
        invoice.status_note,
        invoice.failure_code,
        invoice.failure_reason,
        round(invoice.refund_amount or 0.0, 2),
        invoice.gateway_reference_id,
        invoice.processor_event_at.isoformat() if invoice.processor_event_at else None,
    )


def _resolve_billing_audit_filters():
    audit_status = (request.args.get('audit_status') or '').strip().lower()
    audit_actor = (request.args.get('audit_actor') or '').strip()
    audit_invoice = (request.args.get('audit_invoice') or '').strip()

    if audit_status == 'all':
        audit_status = ''
    if audit_actor.lower() == 'all':
        audit_actor = ''

    if audit_status and audit_status not in BillingInvoice.ALLOWED_STATUSES:
        return None, 'audit_status must be one of paid, pending, failed, or refunded'

    return {
        'status': audit_status,
        'actor': audit_actor,
        'invoice': audit_invoice,
    }, None


def _build_billing_audit_query(start_date, end_date, audit_filters=None, include_actor_filter=True):
    audit_filters = audit_filters or {}
    query = BillingAuditLog.query.join(BillingInvoice, BillingAuditLog.invoice_id == BillingInvoice.id).filter(
        BillingAuditLog.created_at >= start_date,
        BillingAuditLog.created_at < end_date,
    )

    if audit_filters.get('status'):
        query = query.filter(BillingAuditLog.to_status == audit_filters['status'])
    if include_actor_filter and audit_filters.get('actor'):
        query = query.filter(func.lower(BillingAuditLog.actor_username) == audit_filters['actor'].lower())
    if audit_filters.get('invoice'):
        query = query.filter(func.lower(BillingInvoice.invoice_number).like(f"%{audit_filters['invoice'].lower()}%"))

    return query


def _build_billing_audit_export(start_date, end_date, period_days, is_custom_range, audit_filters):
    audit_entries = _build_billing_audit_query(start_date, end_date, audit_filters).order_by(
        BillingAuditLog.created_at.desc()
    ).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Created At', 'Invoice Number', 'User ID', 'Admin Username', 'Admin Email', 'From Status', 'To Status', 'Note'])
    for entry in audit_entries:
        writer.writerow([
            _format_admin_datetime(entry.created_at) or '',
            entry.invoice.invoice_number if entry.invoice else '',
            entry.user_id,
            entry.actor_username or '',
            entry.actor_email or '',
            entry.from_status or '',
            entry.to_status or '',
            entry.status_note or '',
        ])

    if is_custom_range:
        file_suffix = f"{_format_admin_date(start_date)}_to_{_format_admin_date(end_date - timedelta(days=1))}"
    else:
        file_suffix = f"{period_days}d"

    return BytesIO(output.getvalue().encode('utf-8')), f'billing-audit-{file_suffix}.csv'


def _resolve_billing_window():
    start_arg = request.args.get('start_date', '').strip()
    end_arg = request.args.get('end_date', '').strip()

    if start_arg or end_arg:
        if not start_arg or not end_arg:
            return None, None, None, None, 'Both start_date and end_date are required for a custom range'

        start_date = _parse_iso_date(start_arg)
        end_date = _parse_iso_date(end_arg)
        if not start_date or not end_date:
            return None, None, None, None, 'Dates must use YYYY-MM-DD format'
        if start_date > end_date:
            return None, None, None, None, 'start_date must be on or before end_date'

        period_days = (end_date.date() - start_date.date()).days + 1
        if period_days > 366:
            return None, None, None, None, 'Custom billing ranges are limited to 366 days'

        return start_date, end_date + timedelta(days=1), period_days, True, None

    days = request.args.get('days', 30, type=int)
    days = max(1, min(days, 365))
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    return start_date, end_date, days, False, None

# ============================================================================
# USER MANAGEMENT
# ============================================================================

@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users with pagination and filtering."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')
    plan = request.args.get('plan')
    is_active = request.args.get('is_active')
    
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    if plan:
        query = query.filter_by(plan=plan)
    if is_active is not None:
        query = query.filter_by(is_active=is_active in ['true', 'True', '1'])
    
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page,
        'users': [_serialize_admin_user_list_item(user) for user in pagination.items]
    }), 200

@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get user details."""
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'user': user.to_dict(),
        'conversions_count': user.conversions.count(),
        'total_processed_gb': db.session.query(
            func.sum(Conversion.output_size)
        ).filter_by(user_id=user_id).scalar() or 0 / (1024**3),
        'subscription': user.subscription.to_dict() if user.subscription else None,
    }), 200

@bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user details."""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['first_name', 'last_name', 'plan', 'quota_gb', 'role', 'is_active', 'is_verified']
    
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': _serialize_admin_user_list_item(user)
    }), 200

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    
    # Delete associated data (cascade handled in model)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """Reset user password."""
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}
    
    new_password = data.get('new_password') or _generate_temporary_password()
    if len(new_password) < 8:
        return jsonify({'error': 'new_password must be at least 8 characters'}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'message': 'Password reset successfully',
        'temporaryPassword': new_password if 'new_password' not in data else None,
    }), 200


@bp.route('/users/<int:user_id>/reset-usage', methods=['POST'])
@admin_required
def reset_user_usage(user_id):
    """Reset tracked storage usage for a user."""
    user = User.query.get_or_404(user_id)
    user.used_gb = 0
    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'message': 'Usage reset successfully',
        'user': _serialize_admin_user_list_item(user),
    }), 200

# ============================================================================
# CONVERSION ANALYTICS
# ============================================================================

@bp.route('/conversions', methods=['GET'])
@admin_required
def get_conversions():
    """Get all conversions with pagination and filtering."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    user_id = request.args.get('user_id', type=int)
    format_type = request.args.get('format')
    
    query = Conversion.query
    
    if status:
        query = query.filter_by(status=status)
    if user_id:
        query = query.filter_by(user_id=user_id)
    if format_type:
        query = query.filter_by(output_format=format_type)
    
    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page,
        'conversions': [c.to_dict() for c in pagination.items]
    }), 200

@bp.route('/conversions/stats', methods=['GET'])
@admin_required
def get_conversion_stats():
    """Get conversion statistics."""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    total_conversions = Conversion.query.filter(
        Conversion.created_at >= start_date
    ).count()
    
    successful = Conversion.query.filter(
        Conversion.created_at >= start_date,
        Conversion.status == 'completed'
    ).count()
    
    failed = Conversion.query.filter(
        Conversion.created_at >= start_date,
        Conversion.status == 'failed'
    ).count()
    
    total_input_size = db.session.query(func.sum(Conversion.input_size)).filter(
        Conversion.created_at >= start_date
    ).scalar() or 0
    
    total_output_size = db.session.query(func.sum(Conversion.output_size)).filter(
        Conversion.created_at >= start_date
    ).scalar() or 0
    
    # Popular formats
    popular_formats = db.session.query(
        Conversion.output_format,
        func.count(Conversion.id).label('count')
    ).filter(
        Conversion.created_at >= start_date,
        Conversion.status == 'completed'
    ).group_by(Conversion.output_format).order_by(
        func.count(Conversion.id).desc()
    ).limit(10).all()
    
    return jsonify({
        'period_days': days,
        'total_conversions': total_conversions,
        'successful_conversions': successful,
        'failed_conversions': failed,
        'success_rate': round((successful / total_conversions * 100), 2) if total_conversions > 0 else 0,
        'total_input_size_gb': round(total_input_size / (1024**3), 2),
        'total_output_size_gb': round(total_output_size / (1024**3), 2),
        'popular_formats': [
            {'format': fmt, 'count': cnt} for fmt, cnt in popular_formats
        ]
    }), 200


@bp.route('/conversions/monitoring', methods=['GET'])
@admin_required
def get_conversion_monitoring():
    """Get live conversion operations data for the admin dashboard."""
    limit = request.args.get('limit', 100, type=int) or 100
    limit = max(10, min(limit, 250))

    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day)

    queue_size = Conversion.query.filter_by(status='pending').count()
    running_jobs = Conversion.query.filter_by(status='processing').count()

    today_query = Conversion.query.filter(Conversion.created_at >= today_start)
    completed_today = today_query.filter(Conversion.status == 'completed').count()
    failed_today = today_query.filter(Conversion.status == 'failed').count()
    total_today = today_query.count()

    avg_processing_seconds = db.session.query(func.avg(Conversion.processing_time)).filter(
        Conversion.created_at >= today_start,
        Conversion.status == 'completed',
        Conversion.processing_time.isnot(None),
    ).scalar() or 0

    recent_rows = db.session.query(Conversion, User).outerjoin(User, User.id == Conversion.user_id).order_by(
        Conversion.created_at.desc()
    ).limit(limit).all()

    jobs = [_serialize_conversion_monitoring_job(conversion, user) for conversion, user in recent_rows]

    success_denominator = completed_today + failed_today
    success_rate = round((completed_today / success_denominator) * 100, 2) if success_denominator else 0.0

    return jsonify({
        'generatedAt': _format_monitoring_timestamp(now),
        'stats': {
            'queueSize': queue_size,
            'runningJobs': running_jobs,
            'failedJobs': failed_today,
            'totalToday': total_today,
            'completedToday': completed_today,
            'successRate': success_rate,
            'avgProcessingSeconds': round(float(avg_processing_seconds), 2),
        },
        'filters': {
            'all': len(jobs),
            'failed': sum(1 for job in jobs if job['status'] == 'failed'),
            'large': sum(1 for job in jobs if job['isLarge']),
            'slow': sum(1 for job in jobs if job['isSlow']),
        },
        'jobs': jobs,
    }), 200


@bp.route('/analytics/overview', methods=['GET'])
@admin_required
def get_admin_analytics_overview():
    """Get live admin analytics data for dashboard, metrics, traffic, and alerts pages."""
    days = request.args.get('days', 7, type=int) or 7
    return jsonify(_get_admin_analytics_overview(days=days)), 200


@bp.route('/activity-feed', methods=['GET'])
@admin_required
def get_admin_activity_feed():
    """Get recent admin activity and audit events derived from persisted backend records."""
    try:
        period_days = request.args.get('period_days', 30, type=int)
        limit = request.args.get('limit', 200, type=int)
        filters = {
            'userId': request.args.get('user_id', '').strip(),
            'action': request.args.get('action', '').strip(),
            'severity': request.args.get('severity', '').strip(),
            'status': request.args.get('status', '').strip(),
            'startDate': request.args.get('start_date', '').strip(),
            'endDate': request.args.get('end_date', '').strip(),
        }

        events = _build_admin_activity_events(period_days=period_days, limit=max(limit * 2, 50))
        filtered_events = _filter_admin_activity_events(events, filters)[:limit]

        return jsonify({
            'entries': filtered_events,
            'count': len(filtered_events),
            'stats': _build_activity_stats(filtered_events),
            'availableActions': sorted({event['action'] for event in events if event.get('action')}),
            'generatedAt': _format_monitoring_timestamp(datetime.now(timezone.utc)),
        }), 200
    except Exception as exc:
        current_app.logger.error(f"Error loading admin activity feed: {exc}")
        return jsonify({'error': 'Failed to load admin activity feed'}), 500


@bp.route('/api-monitoring', methods=['GET'])
@admin_required
def get_api_monitoring():
    """Get live API monitoring data for the admin dashboard."""
    return jsonify(_get_api_monitoring_payload()), 200


@bp.route('/storage/overview', methods=['GET'])
@admin_required
def get_storage_overview():
    """Get live storage usage and cleanup information for the admin dashboard."""
    return jsonify(_get_storage_management_payload()), 200


@bp.route('/storage/cleanup', methods=['POST'])
@admin_required
def cleanup_storage_uploads():
    """Purge stale upload chunk directories."""
    payload = request.get_json(silent=True) or {}
    result = _purge_upload_chunks(payload.get('olderThanSeconds'))
    return jsonify({
        'message': f"Removed {result['removed']} stale upload staging entr{'y' if result['removed'] == 1 else 'ies'}.",
        **result,
    }), 200


@bp.route('/storage/reconcile', methods=['POST'])
@admin_required
def reconcile_storage_references():
    """Clear stale conversion file references that point to missing files."""
    result = _clear_stale_conversion_references()
    return jsonify({
        'message': f"Cleared {result['totalCleared']} stale conversion file reference(s).",
        **result,
    }), 200


@bp.route('/automation/overview', methods=['GET'])
@admin_required
def get_automation_overview():
    """Get workflow automation status and summary metrics."""
    return jsonify(_build_automation_payload()), 200


@bp.route('/automation/workflows/<workflow_id>/pause', methods=['POST'])
@admin_required
def pause_automation_workflow(workflow_id):
    """Pause a tracked admin automation workflow."""
    state = _load_admin_state()
    workflow = _find_state_item(state.get('automation', {}).get('workflows', []), workflow_id)
    if not workflow:
        return jsonify({'error': 'Workflow not found'}), 404

    workflow['status'] = 'paused'
    workflow['nextRunAt'] = None
    _append_workflow_log(state, workflow_id, 'warning', f"Workflow '{workflow['name']}' paused by admin.", 'warning')
    _append_admin_state_activity_event(state, 'workflow-paused', 'workflow', workflow_id, workflow['name'], {
        'type': workflow.get('type'),
    }, severity='warning', status='success', user_name=getattr(request.current_user, 'username', 'admin'))
    _save_admin_state(state)

    return jsonify({
        'message': f"Paused workflow {workflow['name']}.",
        'workflow': _serialize_admin_workflow(workflow),
    }), 200


@bp.route('/automation/workflows/<workflow_id>/resume', methods=['POST'])
@admin_required
def resume_automation_workflow(workflow_id):
    """Resume a tracked admin automation workflow."""
    state = _load_admin_state()
    workflow = _find_state_item(state.get('automation', {}).get('workflows', []), workflow_id)
    if not workflow:
        return jsonify({'error': 'Workflow not found'}), 404

    workflow['status'] = 'running'
    if not workflow.get('realtime'):
        workflow['nextRunAt'] = _admin_time_plus(hours=1)
    _append_workflow_log(state, workflow_id, 'info', f"Workflow '{workflow['name']}' resumed by admin.")
    _append_admin_state_activity_event(state, 'workflow-resumed', 'workflow', workflow_id, workflow['name'], {
        'type': workflow.get('type'),
    }, severity='info', status='success', user_name=getattr(request.current_user, 'username', 'admin'))
    _save_admin_state(state)

    return jsonify({
        'message': f"Resumed workflow {workflow['name']}.",
        'workflow': _serialize_admin_workflow(workflow),
    }), 200


@bp.route('/automation/workflows/<workflow_id>/logs', methods=['GET'])
@admin_required
def get_automation_workflow_logs(workflow_id):
    """Get logs for a tracked admin automation workflow."""
    state = _load_admin_state()
    workflow = _find_state_item(state.get('automation', {}).get('workflows', []), workflow_id)
    if not workflow:
        return jsonify({'error': 'Workflow not found'}), 404

    logs = [
        {
            **entry,
            'timestampLabel': _format_state_timestamp(entry.get('timestamp')),
        }
        for entry in state.get('automation', {}).get('logs', [])
        if entry.get('workflowId') == workflow_id
    ]

    return jsonify({
        'workflow': _serialize_admin_workflow(workflow),
        'logs': sorted(logs, key=lambda item: item.get('timestamp') or '', reverse=True),
    }), 200


@bp.route('/report-schedules', methods=['GET'])
@admin_required
def get_report_schedules():
    """Get persisted admin report schedules."""
    return jsonify(_build_report_schedules_payload()), 200


@bp.route('/report-schedules', methods=['POST'])
@admin_required
def create_report_schedule():
    """Create a persisted admin report schedule."""
    payload = request.get_json(silent=True) or {}
    report_name = (payload.get('reportName') or '').strip()
    frequency = (payload.get('frequency') or 'daily').strip().lower()
    time_value = (payload.get('time') or '09:00').strip()
    format_value = (payload.get('format') or 'pdf').strip().lower()

    if not report_name:
        return jsonify({'error': 'reportName is required'}), 400
    if frequency not in {'daily', 'weekly', 'monthly'}:
        return jsonify({'error': 'frequency must be daily, weekly, or monthly'}), 400
    if format_value not in {'pdf', 'excel', 'csv'}:
        return jsonify({'error': 'format must be pdf, excel, or csv'}), 400

    try:
        recipients = _validate_email_recipients(payload.get('recipients') or [])
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    if not recipients:
        return jsonify({'error': 'At least one recipient is required'}), 400

    state = _load_admin_state()
    schedule = {
        'id': f"SCH-{secrets.token_hex(3).upper()}",
        'reportName': report_name,
        'frequency': frequency,
        'time': time_value,
        'recipients': recipients,
        'format': format_value,
        'enabled': bool(payload.get('enabled', True)),
        'includeCharts': bool(payload.get('includeCharts', True)),
        'createdAt': _admin_now().isoformat(),
        'updatedAt': _admin_now().isoformat(),
        'lastRunAt': None,
        'nextRunAt': _calculate_schedule_next_run(frequency, time_value),
        'testSentAt': None,
    }
    state.setdefault('reportScheduling', {}).setdefault('schedules', []).append(schedule)
    _append_admin_state_activity_event(state, 'report-schedule-created', 'report_schedule', schedule['id'], schedule['reportName'], {
        'frequency': frequency,
        'format': format_value,
        'recipients': recipients,
    }, user_name=getattr(request.current_user, 'username', 'admin'))
    _save_admin_state(state)

    return jsonify({
        'message': f"Created schedule {schedule['reportName']}.",
        'schedule': _serialize_report_schedule(schedule),
    }), 201


@bp.route('/report-schedules/<schedule_id>', methods=['PUT'])
@admin_required
def update_report_schedule(schedule_id):
    """Update a persisted admin report schedule."""
    payload = request.get_json(silent=True) or {}
    state = _load_admin_state()
    schedule = _find_state_item(state.get('reportScheduling', {}).get('schedules', []), schedule_id)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404

    report_name = (payload.get('reportName', schedule.get('reportName')) or '').strip()
    frequency = (payload.get('frequency', schedule.get('frequency')) or 'daily').strip().lower()
    time_value = (payload.get('time', schedule.get('time')) or '09:00').strip()
    format_value = (payload.get('format', schedule.get('format')) or 'pdf').strip().lower()

    if not report_name:
        return jsonify({'error': 'reportName is required'}), 400

    try:
        recipients = _validate_email_recipients(payload.get('recipients', schedule.get('recipients', [])))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    schedule.update({
        'reportName': report_name,
        'frequency': frequency,
        'time': time_value,
        'recipients': recipients,
        'format': format_value,
        'enabled': bool(payload.get('enabled', schedule.get('enabled', True))),
        'includeCharts': bool(payload.get('includeCharts', schedule.get('includeCharts', True))),
        'updatedAt': _admin_now().isoformat(),
        'nextRunAt': _calculate_schedule_next_run(frequency, time_value),
    })
    _append_admin_state_activity_event(state, 'report-schedule-updated', 'report_schedule', schedule['id'], schedule['reportName'], {
        'frequency': frequency,
        'format': format_value,
        'enabled': schedule['enabled'],
    }, severity='warning', user_name=getattr(request.current_user, 'username', 'admin'))
    _save_admin_state(state)

    return jsonify({
        'message': f"Updated schedule {schedule['reportName']}.",
        'schedule': _serialize_report_schedule(schedule),
    }), 200


@bp.route('/report-schedules/<schedule_id>', methods=['DELETE'])
@admin_required
def delete_report_schedule(schedule_id):
    """Delete a persisted admin report schedule."""
    state = _load_admin_state()
    schedules = state.get('reportScheduling', {}).get('schedules', [])
    schedule = _find_state_item(schedules, schedule_id)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404

    state['reportScheduling']['schedules'] = [item for item in schedules if item.get('id') != schedule_id]
    _append_admin_state_activity_event(state, 'report-schedule-deleted', 'report_schedule', schedule_id, schedule.get('reportName'), {}, severity='warning', user_name=getattr(request.current_user, 'username', 'admin'))
    _save_admin_state(state)

    return jsonify({'message': f"Deleted schedule {schedule.get('reportName', schedule_id)}."}), 200


@bp.route('/report-schedules/<schedule_id>/test', methods=['POST'])
@admin_required
def test_report_schedule(schedule_id):
    """Record a test send for a persisted admin report schedule."""
    state = _load_admin_state()
    schedule = _find_state_item(state.get('reportScheduling', {}).get('schedules', []), schedule_id)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404

    schedule['testSentAt'] = _admin_now().isoformat()
    schedule['updatedAt'] = _admin_now().isoformat()
    _append_admin_state_activity_event(state, 'report-schedule-tested', 'report_schedule', schedule_id, schedule['reportName'], {
        'recipients': schedule.get('recipients', []),
        'format': schedule.get('format'),
    }, user_name=getattr(request.current_user, 'username', 'admin'))
    _save_admin_state(state)

    return jsonify({
        'message': f"Recorded a test dispatch for {schedule['reportName']} to {len(schedule.get('recipients', []))} recipient(s).",
        'schedule': _serialize_report_schedule(schedule),
    }), 200


@bp.route('/security/overview', methods=['GET'])
@admin_required
def get_security_overview():
    """Get persisted security controls and incident summary."""
    return jsonify(_build_security_payload()), 200


@bp.route('/security/blocked-ips', methods=['POST'])
@admin_required
def create_security_blocked_ip():
    """Add a blocked IP entry to the persisted admin security controls."""
    payload = request.get_json(silent=True) or {}
    ip_value = (payload.get('ip') or '').strip()
    reason = (payload.get('reason') or 'Manual block').strip()
    severity = (payload.get('severity') or 'medium').strip().lower()

    try:
        ipaddress.ip_address(ip_value)
    except ValueError:
        return jsonify({'error': 'A valid IP address is required'}), 400

    if severity not in {'low', 'medium', 'high', 'critical'}:
        return jsonify({'error': 'severity must be low, medium, high, or critical'}), 400

    state = _load_admin_state()
    blocked_ips = state.setdefault('security', {}).setdefault('blockedIps', [])
    if any(entry.get('ip') == ip_value for entry in blocked_ips):
        return jsonify({'error': 'IP address is already blocked'}), 409

    block = {
        'id': f"BLK-{secrets.token_hex(3).upper()}",
        'ip': ip_value,
        'reason': reason,
        'blockedDate': _admin_now().isoformat(),
        'severity': severity,
        'source': 'manual',
    }
    blocked_ips.append(block)
    _append_admin_state_activity_event(state, 'security-ip-blocked', 'security_block', block['id'], ip_value, {
        'reason': reason,
        'severity': severity,
    }, severity='warning' if severity in {'medium', 'high'} else severity, user_name=getattr(request.current_user, 'username', 'admin'))
    _save_admin_state(state)

    return jsonify({
        'message': f'Blocked IP {ip_value}.',
        'block': _serialize_security_block(block),
    }), 201


@bp.route('/security/blocked-ips/<block_id>', methods=['DELETE'])
@admin_required
def delete_security_blocked_ip(block_id):
    """Remove a blocked IP entry from persisted admin security controls."""
    state = _load_admin_state()
    blocked_ips = state.setdefault('security', {}).setdefault('blockedIps', [])
    block = _find_state_item(blocked_ips, block_id)
    if not block:
        return jsonify({'error': 'Blocked IP entry not found'}), 404

    state['security']['blockedIps'] = [entry for entry in blocked_ips if entry.get('id') != block_id]
    _append_admin_state_activity_event(state, 'security-ip-unblocked', 'security_block', block_id, block.get('ip'), {
        'reason': block.get('reason'),
    }, user_name=getattr(request.current_user, 'username', 'admin'))
    _save_admin_state(state)

    return jsonify({'message': f"Unblocked IP {block.get('ip')}"}), 200


@bp.route('/security/rate-limit', methods=['PUT'])
@admin_required
def update_security_rate_limit():
    """Update persisted admin-side rate limit guardrail settings."""
    payload = request.get_json(silent=True) or {}

    try:
        default_limit = int(payload.get('defaultLimit'))
        burst_allowance = int(payload.get('burstAllowance'))
    except (TypeError, ValueError):
        return jsonify({'error': 'defaultLimit and burstAllowance must be integers'}), 400

    window_size = (payload.get('windowSize') or '1 hour').strip()
    if default_limit < 1 or burst_allowance < 0:
        return jsonify({'error': 'Rate limit values must be positive'}), 400

    state = _load_admin_state()
    state.setdefault('security', {})['rateLimit'] = {
        'defaultLimit': default_limit,
        'windowSize': window_size,
        'burstAllowance': burst_allowance,
        'updatedAt': _admin_now().isoformat(),
    }
    _append_admin_state_activity_event(state, 'security-rate-limit-updated', 'security_policy', 'default-rate-limit', 'Default rate limit', {
        'defaultLimit': default_limit,
        'windowSize': window_size,
        'burstAllowance': burst_allowance,
    }, severity='warning', user_name=getattr(request.current_user, 'username', 'admin'))
    _save_admin_state(state)

    return jsonify({
        'message': f'Updated admin rate-limit guardrails to {default_limit} requests per {window_size}.',
        'rateLimit': _build_security_payload()['rateLimit'],
    }), 200

# ============================================================================
# PLATFORM STATISTICS
# ============================================================================

@bp.route('/stats', methods=['GET'])
@admin_required
def get_platform_stats():
    """Get overall platform statistics."""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    verified_users = User.query.filter_by(is_verified=True).count()
    
    # User distribution by plan
    plan_distribution = db.session.query(
        User.plan,
        func.count(User.id).label('count')
    ).group_by(User.plan).all()
    
    # User distribution by role
    role_distribution = db.session.query(
        User.role,
        func.count(User.id).label('count')
    ).group_by(User.role).all()
    
    # Total conversions
    total_conversions = Conversion.query.count()
    total_storage_used = db.session.query(
        func.sum(User.used_gb)
    ).scalar() or 0
    
    # Revenue
    monthly_subscriptions = Subscription.query.filter(
        Subscription.is_active == True,
        Subscription.plan != 'free'
    ).all()
    
    mrr = sum(sub.price_per_month for sub in monthly_subscriptions)
    
    return jsonify({
        'users': {
            'total': total_users,
            'active': active_users,
            'verified': verified_users,
            'plan_distribution': [
                {'plan': plan, 'count': count} for plan, count in plan_distribution
            ],
            'role_distribution': [
                {'role': role, 'count': count} for role, count in role_distribution
            ]
        },
        'conversions': {
            'total': total_conversions
        },
        'storage': {
            'total_used_gb': round(total_storage_used, 2)
        },
        'revenue': {
            'monthly_recurring_revenue': round(mrr, 2),
            'active_subscriptions': len(monthly_subscriptions)
        }
    }), 200


# ============================================================================
# BILLING ANALYTICS
# ============================================================================

@bp.route('/billing/overview', methods=['GET'])
@admin_required
def get_billing_overview():
    """Get billing analytics, invoices, and plan-change activity."""
    start_date, end_date, period_days, is_custom_range, error = _resolve_billing_window()
    if error:
        return jsonify({'error': error}), 400

    audit_filters, audit_error = _resolve_billing_audit_filters()
    if audit_error:
        return jsonify({'error': audit_error}), 400

    invoice_page, invoice_per_page = _parse_pagination('invoice', DEFAULT_INVOICE_PAGE_SIZE)
    audit_page, audit_per_page = _parse_pagination('audit', DEFAULT_AUDIT_PAGE_SIZE)

    period_invoices_query = BillingInvoice.query.filter(
        BillingInvoice.issued_at >= start_date,
        BillingInvoice.issued_at < end_date,
    )
    period_paid_invoices_query = period_invoices_query.filter(BillingInvoice.status == BillingInvoice.STATUS_PAID)
    period_pending_invoices_query = period_invoices_query.filter(BillingInvoice.status == BillingInvoice.STATUS_PENDING)
    period_failed_invoices_query = period_invoices_query.filter(BillingInvoice.status == BillingInvoice.STATUS_FAILED)
    period_refunded_invoices_query = period_invoices_query.filter(BillingInvoice.status == BillingInvoice.STATUS_REFUNDED)
    plan_change_query = BillingInvoice.query.filter(
        BillingInvoice.description.like('Plan changed from %'),
        BillingInvoice.issued_at >= start_date,
        BillingInvoice.issued_at < end_date,
    )

    mrr = db.session.query(func.sum(Subscription.price_per_month)).filter(
        Subscription.is_active == True,
        Subscription.plan != 'free'
    ).scalar() or 0.0

    active_paid_subscriptions = Subscription.query.filter(
        Subscription.is_active == True,
        Subscription.plan != 'free'
    ).count()

    next_renewal = db.session.query(func.min(Subscription.renewal_date)).filter(
        Subscription.is_active == True,
        Subscription.plan != 'free',
        Subscription.renewal_date.isnot(None),
    ).scalar()

    conversions_used = db.session.query(func.sum(Subscription.conversions_used_this_month)).filter(
        Subscription.is_active == True
    ).scalar() or 0
    conversion_capacity = db.session.query(func.sum(Subscription.monthly_conversion_limit)).filter(
        Subscription.is_active == True
    ).scalar() or 0
    storage_used = db.session.query(func.sum(User.used_gb)).scalar() or 0
    storage_capacity = db.session.query(func.sum(User.quota_gb)).scalar() or 0

    recent_invoices = period_invoices_query.order_by(BillingInvoice.issued_at.desc()).paginate(
        page=invoice_page,
        per_page=invoice_per_page,
        error_out=False,
    )
    recent_plan_changes = plan_change_query.order_by(BillingInvoice.issued_at.desc()).limit(10).all()
    audit_query = _build_billing_audit_query(start_date, end_date, audit_filters)
    audit_actor_query = _build_billing_audit_query(start_date, end_date, audit_filters, include_actor_filter=False)
    recent_status_changes = audit_query.order_by(BillingAuditLog.created_at.desc()).paginate(
        page=audit_page,
        per_page=audit_per_page,
        error_out=False,
    )
    audit_matching_count = audit_query.count()
    available_audit_actors = [
        actor_name for actor_name, in audit_actor_query.with_entities(BillingAuditLog.actor_username)
        .filter(BillingAuditLog.actor_username.isnot(None))
        .distinct()
        .order_by(BillingAuditLog.actor_username.asc())
        .all()
    ]
    plan_distribution = db.session.query(
        Subscription.plan,
        func.count(Subscription.id).label('count')
    ).filter(Subscription.is_active == True).group_by(Subscription.plan).all()

    return jsonify({
        'summary': {
            'periodDays': period_days,
            'periodStart': _format_admin_date(start_date),
            'periodEnd': _format_admin_date(end_date - timedelta(days=1) if is_custom_range else end_date),
            'isCustomRange': bool(is_custom_range),
            'monthlyRecurringRevenue': round(mrr, 2),
            'activePaidSubscriptions': active_paid_subscriptions,
            'totalInvoices': BillingInvoice.query.count(),
            'paidInvoices': period_paid_invoices_query.count(),
            'pendingInvoices': period_pending_invoices_query.count(),
            'failedInvoices': period_failed_invoices_query.count(),
            'refundedInvoices': period_refunded_invoices_query.count(),
            'invoicesDuringPeriod': period_invoices_query.count(),
            'billedDuringPeriod': round(db.session.query(func.sum(BillingInvoice.amount)).filter(
                BillingInvoice.issued_at >= start_date,
                BillingInvoice.issued_at < end_date,
                BillingInvoice.status == 'paid',
            ).scalar() or 0.0, 2),
            'planChangesDuringPeriod': plan_change_query.count(),
            'nextRenewalDate': _format_admin_date(next_renewal),
        },
        'usage': {
            'conversionsUsedThisMonth': int(conversions_used),
            'conversionsCapacity': int(conversion_capacity),
            'storageUsedGb': round(float(storage_used), 2),
            'storageCapacityGb': round(float(storage_capacity), 2),
        },
        'planDistribution': [
            {'plan': plan.title(), 'count': count} for plan, count in plan_distribution
        ],
        'recentInvoices': [_serialize_admin_invoice(invoice) for invoice in recent_invoices.items],
        'invoicePagination': _serialize_pagination(recent_invoices),
        'recentPlanChanges': [
            item for item in (_serialize_plan_change(invoice) for invoice in recent_plan_changes) if item
        ],
        'recentStatusChanges': [_serialize_billing_audit_log(entry) for entry in recent_status_changes.items],
        'auditPagination': _serialize_pagination(recent_status_changes),
        'auditFilters': {
            'status': audit_filters['status'] or 'all',
            'actor': audit_filters['actor'] or 'all',
            'invoice': audit_filters['invoice'] or '',
            'matchingCount': audit_matching_count,
            'availableActors': available_audit_actors,
        },
        'providerSync': {
            'endpoint': _get_public_billing_provider_endpoint(),
            'secretConfigured': bool(current_app.config.get('BILLING_PROVIDER_WEBHOOK_SECRET')),
            'signatureHeader': 'X-DocPro-Billing-Signature',
            'supportedProviders': ['generic', 'stripe'],
            'stripeMetadataKeys': ['docpro_invoice_id', 'invoice_id', 'docpro_invoice_number', 'invoice_number'],
            'supportedEventTypes': [
                'invoice.paid',
                'invoice.pending',
                'invoice.payment_failed',
                'payment.succeeded',
                'payment.pending',
                'payment.failed',
                'charge.succeeded',
                'charge.failed',
                'charge.refunded',
                'refund.succeeded',
            ],
        },
    }), 200


@bp.route('/billing/audit/export', methods=['GET'])
@admin_required
def export_billing_audit():
    """Export filtered billing audit activity as CSV."""
    start_date, end_date, period_days, is_custom_range, error = _resolve_billing_window()
    if error:
        return jsonify({'error': error}), 400

    audit_filters, audit_error = _resolve_billing_audit_filters()
    if audit_error:
        return jsonify({'error': audit_error}), 400

    stream, filename = _build_billing_audit_export(start_date, end_date, period_days, is_custom_range, audit_filters)
    return send_file(stream, as_attachment=True, download_name=filename, mimetype='text/csv')


@bp.route('/billing/invoices/<int:invoice_id>/download', methods=['GET'])
@admin_required
def download_billing_invoice(invoice_id):
    """Download any persisted invoice as an admin."""
    stream, filename = SubscriptionService.render_invoice_for_admin(invoice_id)
    return send_file(stream, as_attachment=True, download_name=filename, mimetype='text/plain')


@bp.route('/billing/invoices/<int:invoice_id>/status', methods=['POST'])
@admin_required
def update_billing_invoice_status(invoice_id):
    """Update persisted invoice status for billing operations."""
    payload = request.get_json(silent=True) or {}
    invoice = BillingInvoice.query.get_or_404(invoice_id)
    previous_status = invoice.status

    try:
        _apply_invoice_status(invoice, payload)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    _record_billing_audit(invoice, request.current_user, previous_status, invoice.status, payload.get('status_note'))

    db.session.commit()
    return jsonify({
        'message': f'Invoice {invoice.invoice_number} updated to {invoice.status}.',
        'invoice': _serialize_admin_invoice(invoice),
    }), 200


@bp.route('/billing/provider-events', methods=['POST'])
def ingest_billing_provider_event():
    """Ingest signed provider billing events and map them onto persisted invoices."""
    raw_body = request.get_data(cache=True) or b''
    is_valid, signature_error = _verify_provider_event_signature(raw_body)
    if not is_valid:
        return jsonify({'error': signature_error}), 401

    payload = request.get_json(silent=True) or {}
    if not payload and raw_body:
        payload = json.loads(raw_body.decode('utf-8'))
    if not payload:
        return jsonify({'error': 'Provider event payload is required'}), 400

    try:
        normalized_payload = _normalize_provider_payload(payload)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    invoice = _resolve_provider_invoice(normalized_payload)
    if not invoice:
        return jsonify({'error': 'No invoice matched the provider event'}), 404

    previous_status = invoice.status
    previous_snapshot = _invoice_state_snapshot(invoice)

    try:
        status_payload = _build_provider_status_payload(normalized_payload)
        _apply_invoice_status(invoice, status_payload)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    next_snapshot = _invoice_state_snapshot(invoice)
    state_changed = previous_snapshot != next_snapshot
    if state_changed:
        _record_billing_system_audit(
            invoice,
            previous_status,
            invoice.status,
            status_payload.get('status_note'),
            action=f'{normalized_payload.get("provider", "generic")}_provider_event_ingested',
        )

    db.session.commit()
    return jsonify({
        'message': 'Provider billing event processed.',
        'applied': state_changed,
        'provider': normalized_payload.get('provider', 'generic'),
        'providerEventId': normalized_payload.get('provider_event_id'),
        'invoice': _serialize_admin_invoice(invoice),
    }), 200

# ============================================================================
# ROLE MANAGEMENT
# ============================================================================

@bp.route('/roles', methods=['GET'])
@admin_required
def get_roles():
    """Get available roles and their permissions."""
    role_definitions = {
        'user': {
            'name': 'User',
            'description': 'Standard customer access with self-service conversion tools.',
            'permissions': [
                'conversions:read',
                'conversions:write',
                'profile:read',
                'profile:write'
            ]
        },
        'moderator': {
            'name': 'Moderator',
            'description': 'Support and operational access for customer issue resolution.',
            'permissions': [
                'users:read',
                'users:support',
                'conversions:read'
            ]
        },
        'admin': {
            'name': 'Administrator',
            'description': 'Full administrative access across the platform.',
            'permissions': [
                '*'
            ]
        }
    }

    role_counts = dict(
        db.session.query(User.role, func.count(User.id))
        .group_by(User.role)
        .all()
    )

    return jsonify({
        'roles': [
            {
                'key': key,
                'userCount': int(role_counts.get(key, 0)),
                **definition,
            }
            for key, definition in role_definitions.items()
        ]
    }), 200

# ============================================================================
# SYSTEM HEALTH
# ============================================================================

@bp.route('/health', methods=['GET'])
@admin_required
def get_system_health():
    """Get system health status."""
    database_component = _get_database_component_health()
    cache_component = _get_cache_component_health()
    storage_component = _get_storage_component_health()
    worker_payload = _get_worker_monitoring_payload()
    metrics = _get_system_metrics_snapshot()

    components = {
        'database': database_component,
        'api': {
            'status': 'healthy',
            'message': 'Admin API responding',
        },
        'cache': cache_component,
        'workers': {
            'status': worker_payload['status'],
            'message': worker_payload['message'],
            'activeWorkers': worker_payload['stats']['activeWorkers'],
            'queueSize': worker_payload['stats']['queueSize'],
        },
        'storage': storage_component,
    }
    overall_status = _combine_statuses(component['status'] for component in components.values())
    alerts = _build_system_alerts(metrics, components, worker_payload)

    return jsonify({
        'status': overall_status,
        'components': components,
        'metrics': metrics,
        'alerts': alerts,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }), 200


@bp.route('/workers', methods=['GET'])
@admin_required
def get_worker_monitoring():
    """Get live Celery worker status for the admin dashboard."""
    worker_payload = _get_worker_monitoring_payload()
    return jsonify({
        **worker_payload,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }), 200
