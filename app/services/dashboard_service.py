"""Live dashboard data services for user and admin dashboards."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from time import perf_counter

from flask import current_app

from app.models import Conversion, Subscription, User, db


class DashboardService:
    """Build live dashboard payloads from persisted application data."""

    PLAN_DETAILS = {
        'free': {
            'description': 'Essential tools for occasional conversions.',
            'features': ['Monthly usage cap', 'Standard storage', 'Community support'],
        },
        'pro': {
            'description': 'Full access to converters for active individual workflows.',
            'features': ['Higher monthly conversion limits', 'Expanded storage quota', 'Priority support'],
        },
        'enterprise': {
            'description': 'High-volume conversion access with enterprise-grade capacity.',
            'features': ['High monthly throughput', 'Large storage allocation', 'Dedicated support path'],
        },
    }

    @staticmethod
    def resolve_output_path(output_path):
        if not output_path:
            return None

        output = Path(output_path)
        workspace_root = Path(current_app.root_path).parent
        candidates = [output]

        if not output.is_absolute():
            candidates.extend([
                Path.cwd() / output,
                workspace_root / output,
                Path(current_app.root_path) / output,
            ])

        normalized = []
        for candidate in candidates:
            resolved = candidate.resolve(strict=False)
            normalized.append(str(resolved))
            if resolved.exists():
                return str(resolved)

        return normalized[-1] if normalized else None

    @staticmethod
    def _format_bytes(size_bytes):
        value = float(size_bytes or 0)
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0

        while value >= 1024 and unit_index < len(units) - 1:
            value /= 1024
            unit_index += 1

        precision = 0 if unit_index == 0 else 1
        return f"{value:.{precision}f} {units[unit_index]}"

    @staticmethod
    def _format_short_date(value):
        if not value:
            return 'N/A'
        return f"{value.strftime('%b')} {value.day}"

    @staticmethod
    def _format_pair(conversion):
        return f"{(conversion.input_format or 'file').upper()} to {(conversion.output_format or 'file').upper()}"

    @staticmethod
    def _serialize_conversion(conversion):
        created_at = conversion.created_at or datetime.now(timezone.utc)
        size_bytes = conversion.output_size or conversion.input_size or 0
        resolved_output_path = DashboardService.resolve_output_path(conversion.output_path)
        can_download = bool(resolved_output_path and os.path.exists(resolved_output_path))
        return {
            'id': conversion.id,
            'filename': conversion.input_filename,
            'from': (conversion.input_format or '').upper(),
            'to': (conversion.output_format or '').upper(),
            'date': DashboardService._format_short_date(created_at),
            'time': created_at.strftime('%H:%M'),
            'status': conversion.status,
            'size': DashboardService._format_bytes(size_bytes),
            'duration': round(float(conversion.processing_time or 0), 1),
            'created_at': created_at.isoformat(),
            'download_count': conversion.download_count or 0,
            'can_download': can_download,
        }

    @staticmethod
    def _delta_text(current_value, previous_value, positive_when='up', unit=''):
        delta = round(float(current_value or 0) - float(previous_value or 0), 1)
        if delta == 0:
            return {'text': 'No change vs previous period', 'direction': 'flat'}

        delta_abs = abs(delta)
        if unit == '%':
            display = f'{delta_abs:.1f}%'
        elif unit == 's':
            display = f'{delta_abs:.1f}s'
        else:
            display = f'{int(delta_abs)}' if float(delta_abs).is_integer() else f'{delta_abs:.1f}'

        if positive_when == 'down':
            return {
                'text': f"{display} {'faster' if delta < 0 else 'slower'} than previous period",
                'direction': 'up' if delta < 0 else 'down',
            }

        prefix = '+' if delta > 0 else '-'
        return {
            'text': f'{prefix}{display} vs previous period',
            'direction': 'up' if delta > 0 else 'down',
        }

    @staticmethod
    def get_user_dashboard(user_id):
        user = User.query.get_or_404(user_id)
        conversions = Conversion.query.filter_by(user_id=user_id).order_by(Conversion.created_at.desc()).all()

        now = datetime.now(timezone.utc)
        month_start = datetime(now.year, now.month, 1)
        previous_month_end = month_start - timedelta(seconds=1)
        previous_month_start = datetime(previous_month_end.year, previous_month_end.month, 1)
        completed = [item for item in conversions if item.status == 'completed']
        monthly = [item for item in conversions if item.created_at and item.created_at >= month_start]
        previous_month = [
            item for item in conversions
            if item.created_at and previous_month_start <= item.created_at < month_start
        ]
        timed = [item.processing_time for item in completed if item.processing_time]
        previous_timed = [item.processing_time for item in previous_month if item.status == 'completed' and item.processing_time]
        pair_counter = Counter(DashboardService._format_pair(item) for item in completed)

        total_input_bytes = sum(item.input_size or 0 for item in completed)
        total_output_bytes = sum(item.output_size or 0 for item in completed)
        derived_storage_gb = round(total_output_bytes / float(1024 ** 3), 2)
        storage_used = round(max(float(user.used_gb or 0), derived_storage_gb), 2)

        subscription = user.subscription
        storage_total = float(
            (subscription.storage_quota_gb if subscription and subscription.storage_quota_gb is not None else None)
            or user.quota_gb
            or 5
        )

        breakdown_counter = defaultdict(int)
        for item in completed:
            label = (item.output_format or item.input_format or 'other').upper()
            breakdown_counter[label] += item.output_size or item.input_size or 0

        total_breakdown = sum(breakdown_counter.values()) or 1
        storage_breakdown = []
        for label, size_bytes in sorted(breakdown_counter.items(), key=lambda entry: entry[1], reverse=True)[:4]:
            storage_breakdown.append({
                'label': label,
                'size': DashboardService._format_bytes(size_bytes),
                'pct': round((size_bytes / total_breakdown) * 100),
            })

        successful_count = len(completed)
        total_count = len(conversions)
        success_rate = round((successful_count / total_count) * 100, 1) if total_count else 0.0
        previous_successful_count = len([item for item in previous_month if item.status == 'completed'])
        previous_total_count = len(previous_month)
        previous_success_rate = round((previous_successful_count / previous_total_count) * 100, 1) if previous_total_count else 0.0
        conversions_saved_mb = round(max(total_input_bytes - total_output_bytes, 0) / float(1024 ** 2), 1)

        avg_time = round(sum(timed) / len(timed), 1) if timed else 0
        previous_avg_time = round(sum(previous_timed) / len(previous_timed), 1) if previous_timed else 0

        plan_code = (subscription.plan if subscription else user.plan or 'free').lower()
        plan_meta = DashboardService.PLAN_DETAILS.get(plan_code, DashboardService.PLAN_DETAILS['free'])
        monthly_limit = subscription.monthly_conversion_limit if subscription else 100
        plan_features = list(plan_meta['features'])
        plan_features.insert(0, f'{int(storage_total)} GB storage quota')
        if monthly_limit:
            plan_features.insert(0, f'{monthly_limit} conversions per month')

        notifications = []
        for item in conversions[:3]:
            label = 'completed' if item.status == 'completed' else item.status.replace('_', ' ')
            notifications.append({
                'id': item.id,
                'title': f"Conversion {label.title()}",
                'meta': f"{item.input_filename} to {(item.output_format or '').upper()} at {DashboardService._format_short_date(item.created_at)} {item.created_at.strftime('%H:%M') if item.created_at else ''}".strip(),
                'icon': '✅' if item.status == 'completed' else '⏳' if item.status in ('pending', 'processing') else '⚠️',
            })

        if not notifications:
            notifications = [
                {
                    'id': 'welcome',
                    'title': 'Dashboard Ready',
                    'meta': 'Start your first conversion to populate live activity.',
                    'icon': '🎯',
                }
            ]

        return {
            'stats': {
                'totalConversions': total_count,
                'conversionsSaved': conversions_saved_mb,
                'averageConversionTime': avg_time,
                'mostUsedTool': pair_counter.most_common(1)[0][0] if pair_counter else 'No conversions yet',
                'filesProcessed': successful_count,
                'successRate': success_rate,
                'monthlyConversions': len(monthly),
                'storageUsed': storage_used,
                'storageTotal': storage_total,
            },
            'insights': {
                'totalConversionsTrend': DashboardService._delta_text(len(monthly), len(previous_month)),
                'averageConversionTimeTrend': DashboardService._delta_text(avg_time, previous_avg_time, positive_when='down', unit='s'),
                'successRateTrend': DashboardService._delta_text(success_rate, previous_success_rate, unit='%'),
                'monthlyConversionsTrend': DashboardService._delta_text(len(monthly), len(previous_month)),
                'filesProcessedTrend': DashboardService._delta_text(successful_count, previous_successful_count),
                'conversionsSavedTrend': {
                    'text': f'{conversions_saved_mb:.1f} MB reduced through completed conversions',
                    'direction': 'up' if conversions_saved_mb > 0 else 'flat',
                },
                'mostUsedToolDetail': f"{pair_counter.most_common(1)[0][1]} completed conversions" if pair_counter else 'Waiting for conversion activity',
            },
            'profile': {
                'joinDate': user.created_at.strftime('%Y-%m-%d') if user.created_at else None,
                'plan': plan_code.title(),
                'nextBillingDate': (
                    subscription.renewal_date.strftime('%Y-%m-%d')
                    if subscription and subscription.renewal_date else 'N/A'
                ),
                'conversionsThisMonth': len(monthly),
                'tasksCompleted': successful_count,
            },
            'planDetails': {
                'name': plan_code.title(),
                'description': plan_meta['description'],
                'features': plan_features,
                'daysUntilRenewal': subscription.days_until_renewal() if subscription else None,
                'maxFileSizeMb': subscription.max_file_size_mb if subscription else None,
                'monthlyLimit': monthly_limit,
            },
            'conversions': [DashboardService._serialize_conversion(item) for item in conversions[:25]],
            'storageBreakdown': storage_breakdown,
            'notifications': notifications,
        }

    @staticmethod
    def get_admin_overview():
        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day)
        yesterday_start = today_start - timedelta(days=1)
        last_24_hours = now - timedelta(hours=24)

        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()

        conversions_today = Conversion.query.filter(Conversion.created_at >= today_start).count()
        conversions_yesterday = Conversion.query.filter(
            Conversion.created_at >= yesterday_start,
            Conversion.created_at < today_start,
        ).count()

        recent_total = Conversion.query.filter(Conversion.created_at >= last_24_hours).count()
        recent_success = Conversion.query.filter(
            Conversion.created_at >= last_24_hours,
            Conversion.status == 'completed',
        ).count()
        success_rate = round((recent_success / recent_total) * 100, 1) if recent_total else 0.0

        active_subscriptions = Subscription.query.filter(
            Subscription.is_active == True,
            Subscription.plan != 'free',
        ).all()
        monthly_recurring_revenue = sum(item.price_per_month or 0 for item in active_subscriptions)
        daily_run_rate = round(monthly_recurring_revenue / 30, 2) if monthly_recurring_revenue else 0.0

        worker_queue = Conversion.query.filter(Conversion.status.in_(['pending', 'processing'])).count()
        server_load = min(100, round(((worker_queue + recent_total) / max(total_users, 1)) * 10, 1)) if total_users else 0

        def build_trend(current_value, previous_value, suffix='vs yesterday'):
            delta = current_value - previous_value
            if delta > 0:
                return f"+{delta} {suffix}", 'up'
            if delta < 0:
                return f"{delta} {suffix}", 'down'
            return f"0 {suffix}", 'flat'

        conversions_trend, conversions_direction = build_trend(conversions_today, conversions_yesterday)
        users_trend, users_direction = build_trend(active_users, total_users - active_users, 'inactive delta')

        cards = [
            {
                'label': 'Conversions Today',
                'value': f"{conversions_today:,}",
                'icon': '🔄',
                'trend': conversions_trend,
                'direction': conversions_direction,
                'color': '#667eea',
            },
            {
                'label': 'Active Users',
                'value': f"{active_users:,}",
                'icon': '👥',
                'trend': users_trend,
                'direction': users_direction,
                'color': '#48bb78',
            },
            {
                'label': '24h Success Rate',
                'value': f"{success_rate}%",
                'icon': '✅',
                'trend': f"{recent_success}/{recent_total or 0} completed",
                'direction': 'up' if success_rate >= 95 else 'down',
                'color': '#38b2ac',
            },
            {
                'label': 'Daily Revenue Run Rate',
                'value': f"${daily_run_rate:,.2f}",
                'icon': '💰',
                'trend': f"MRR ${monthly_recurring_revenue:,.2f}",
                'direction': 'up' if daily_run_rate > 0 else 'flat',
                'color': '#ed8936',
            },
            {
                'label': 'Server Load Index',
                'value': f"{server_load}%",
                'icon': '📡',
                'trend': f"{recent_total} jobs in 24h",
                'direction': 'down' if server_load > 75 else 'up',
                'color': '#9f7aea',
            },
            {
                'label': 'Worker Queue',
                'value': str(worker_queue),
                'icon': '⚙️',
                'trend': 'pending + processing',
                'direction': 'down' if worker_queue > 10 else 'up',
                'color': '#f56565',
            },
        ]

        buckets = []
        for offset in range(11, -1, -1):
            bucket_start = now - timedelta(hours=offset * 2)
            buckets.append({
                'label': bucket_start.strftime('%H:%M'),
                'start': bucket_start,
                'end': bucket_start + timedelta(hours=2),
            })

        recent_conversions = Conversion.query.filter(
            Conversion.created_at >= buckets[0]['start']
        ).all() if buckets else []

        conversions_by_hour = []
        for bucket in buckets:
            count = sum(
                1 for item in recent_conversions
                if item.created_at and bucket['start'] <= item.created_at < bucket['end']
            )
            conversions_by_hour.append(count)

        format_counts = Counter(
            (item.output_format or 'other').upper()
            for item in Conversion.query.filter(Conversion.status == 'completed').all()
        )
        top_formats = format_counts.most_common(4)

        plan_counts = Counter(
            (plan or 'free').title()
            for plan, in db.session.query(User.plan).all()
        )
        plan_distribution = plan_counts.most_common(5)

        services = []

        db_started = perf_counter()
        User.query.limit(1).all()
        db_latency = round((perf_counter() - db_started) * 1000)
        services.append({
            'name': 'Database',
            'latency': f'{db_latency}ms',
            'status': 'Online',
        })

        services.append({
            'name': 'Authentication',
            'latency': 'JWT',
            'status': 'Online',
        })
        services.append({
            'name': 'Workers',
            'latency': f'{worker_queue} queued',
            'status': 'Busy' if worker_queue else 'Online',
        })
        services.append({
            'name': 'Storage',
            'latency': f"{round(sum(user.used_gb or 0 for user in User.query.all()), 2)} GB used",
            'status': 'Online',
        })
        services.append({
            'name': 'SEO Coverage',
            'latency': f"{sum(1 for value in format_counts.values())} formats",
            'status': 'Online',
        })
        services.append({
            'name': 'Background Tasks',
            'latency': 'enabled' if bool(db.session.bind) else 'unavailable',
            'status': 'Online' if bool(db.session.bind) else 'Degraded',
        })

        return {
            'cards': cards,
            'charts': {
                'conversions': {
                    'title': 'Conversions per 2 Hours',
                    'labels': [bucket['label'] for bucket in buckets],
                    'data': conversions_by_hour,
                },
                'formats': {
                    'title': 'Format Distribution',
                    'labels': [label for label, _ in top_formats] or ['No Data'],
                    'data': [count for _, count in top_formats] or [1],
                },
                'plans': {
                    'title': 'User Plan Distribution',
                    'labels': [label for label, _ in plan_distribution] or ['Free'],
                    'data': [count for _, count in plan_distribution] or [0],
                },
            },
            'services': services,
        }