"""Advanced analytics module for DocPro."""
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, and_
from app.models import db, User, Conversion, Subscription
from enum import Enum

class ConversionStatus(Enum):
    """Conversion status enumeration."""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class AnalyticsService:
    """Comprehensive analytics service."""
    
    @staticmethod
    def get_conversion_metrics(days=30, user_id=None):
        """Get conversion metrics for period."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        query = Conversion.query.filter(
            Conversion.created_at >= start_date
        )
        
        if user_id:
            query = query.filter(Conversion.user_id == user_id)
        
        conversions = query.all()
        
        metrics = {
            'period_days': days,
            'total_conversions': len(conversions),
            'successful': len([c for c in conversions if c.status == 'completed']),
            'failed': len([c for c in conversions if c.status == 'failed']),
            'pending': len([c for c in conversions if c.status == 'pending']),
            'cancelled': len([c for c in conversions if c.status == 'cancelled']),
            'success_rate': 0,
            'avg_processing_time': 0,
            'total_input_size': 0,
            'total_output_size': 0,
            'by_format': {}
        }
        
        if conversions:
            metrics['success_rate'] = (metrics['successful'] / len(conversions)) * 100
            
            completed = [c for c in conversions if c.status == 'completed' and c.processing_time]
            if completed:
                metrics['avg_processing_time'] = sum(c.processing_time for c in completed) / len(completed)
            
            metrics['total_input_size'] = sum(c.input_size or 0 for c in conversions)
            metrics['total_output_size'] = sum(c.output_size or 0 for c in conversions)
            
            # Group by format
            for conversion in conversions:
                format_key = f"{conversion.input_format}->{conversion.output_format}"
                if format_key not in metrics['by_format']:
                    metrics['by_format'][format_key] = {
                        'count': 0,
                        'successful': 0,
                        'failed': 0
                    }
                metrics['by_format'][format_key]['count'] += 1
                if conversion.status == 'completed':
                    metrics['by_format'][format_key]['successful'] += 1
                elif conversion.status == 'failed':
                    metrics['by_format'][format_key]['failed'] += 1
        
        return metrics
    
    @staticmethod
    def get_user_metrics(days=30):
        """Get user engagement metrics."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        metrics = {
            'period_days': days,
            'total_users': User.query.count(),
            'new_users': User.query.filter(User.created_at >= start_date).count(),
            'active_users': 0,
            'by_plan': {},
            'retention': 0
        }
        
        # Active users (used service in period)
        active_user_ids = db.session.query(
            func.distinct(Conversion.user_id)
        ).filter(
            Conversion.created_at >= start_date
        ).all()
        
        metrics['active_users'] = len(active_user_ids) if active_user_ids else 0
        
        # By plan
        plan_data = db.session.query(
            Subscription.plan_type,
            func.count(User.id)
        ).join(
            Subscription, User.id == Subscription.user_id
        ).group_by(
            Subscription.plan_type
        ).all()
        
        for plan, count in plan_data:
            metrics['by_plan'][plan] = count
        
        # Retention rate
        if metrics['total_users'] > 0:
            metrics['retention'] = (metrics['active_users'] / metrics['total_users']) * 100
        
        return metrics
    
    @staticmethod
    def get_revenue_metrics(days=30):
        """Get revenue-related metrics."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        subscriptions = Subscription.query.filter(
            Subscription.created_at >= start_date
        ).all()
        
        plan_pricing = {
            'free': 0,
            'pro': 9.99,
            'enterprise': 99.99
        }
        
        metrics = {
            'period_days': days,
            'mrr': 0,  # Monthly Recurring Revenue
            'arpu': 0,  # Average Revenue Per User
            'churn_rate': 0,
            'by_plan': {}
        }
        
        for plan, price in plan_pricing.items():
            count = len([s for s in subscriptions if s.plan_type == plan])
            metrics['by_plan'][plan] = {
                'count': count,
                'monthly_revenue': count * price
            }
            metrics['mrr'] += count * price
        
        # Calculate ARPU
        total_active = sum(p['count'] for p in metrics['by_plan'].values())
        if total_active > 0:
            metrics['arpu'] = metrics['mrr'] / total_active
        
        # Churn rate (users who ended subscription in period)
        cancelled = Subscription.query.filter(
            and_(
                Subscription.cancelled_at >= start_date,
                Subscription.cancelled_at != None
            )
        ).count()
        
        if total_active > 0:
            metrics['churn_rate'] = (cancelled / total_active) * 100
        
        return metrics
    
    @staticmethod
    def get_performance_metrics():
        """Get system performance metrics."""
        conversions = Conversion.query.filter(
            Conversion.status == 'completed'
        ).all()
        
        metrics = {
            'p50_processing_time': 0,
            'p95_processing_time': 0,
            'p99_processing_time': 0,
            'min_processing_time': 0,
            'max_processing_time': 0,
            'slowest_formats': [],
            'fastest_formats': []
        }
        
        if conversions:
            times = sorted([c.processing_time for c in conversions if c.processing_time])
            
            if times:
                metrics['min_processing_time'] = times[0]
                metrics['max_processing_time'] = times[-1]
                
                n = len(times)
                metrics['p50_processing_time'] = times[int(n * 0.5)]
                metrics['p95_processing_time'] = times[int(n * 0.95)] if n >= 20 else times[-1]
                metrics['p99_processing_time'] = times[int(n * 0.99)] if n >= 100 else times[-1]
                
                # Slowest formats
                format_times = {}
                for c in conversions:
                    fmt = f"{c.input_format}->{c.output_format}"
                    if fmt not in format_times:
                        format_times[fmt] = []
                    if c.processing_time:
                        format_times[fmt].append(c.processing_time)
                
                avg_times = {fmt: sum(times) / len(times) for fmt, times in format_times.items()}
                
                slowest = sorted(avg_times.items(), key=lambda x: x[1], reverse=True)[:5]
                fastest = sorted(avg_times.items(), key=lambda x: x[1])[:5]
                
                metrics['slowest_formats'] = [{'format': fmt, 'avg_time': time} for fmt, time in slowest]
                metrics['fastest_formats'] = [{'format': fmt, 'avg_time': time} for fmt, time in fastest]
        
        return metrics
    
    @staticmethod
    def get_platform_stats():
        """Get overall platform statistics."""
        return {
            'conversions': AnalyticsService.get_conversion_metrics(),
            'users': AnalyticsService.get_user_metrics(),
            'revenue': AnalyticsService.get_revenue_metrics(),
            'performance': AnalyticsService.get_performance_metrics(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    def get_format_popularity(days=30, limit=10):
        """Get most popular conversion formats."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        formats = db.session.query(
            func.concat(Conversion.input_format, '->', Conversion.output_format),
            func.count(Conversion.id)
        ).filter(
            Conversion.created_at >= start_date
        ).group_by(
            Conversion.input_format,
            Conversion.output_format
        ).order_by(
            func.count(Conversion.id).desc()
        ).limit(limit).all()
        
        return [{'format': fmt, 'count': count} for fmt, count in formats]
    
    @staticmethod
    def get_user_behavior(user_id, days=30):
        """Get user behavior analytics."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        conversions = Conversion.query.filter(
            and_(
                Conversion.user_id == user_id,
                Conversion.created_at >= start_date
            )
        ).all()
        
        behavior = {
            'user_id': user_id,
            'period_days': days,
            'total_conversions': len(conversions),
            'success_rate': 0,
            'data_processed': 0,
            'avg_conversion_time': 0,
            'most_used_formats': {},
            'last_active': None,
            'daily_activity': {}
        }
        
        if conversions:
            successful = len([c for c in conversions if c.status == 'completed'])
            behavior['success_rate'] = (successful / len(conversions)) * 100
            
            behavior['data_processed'] = sum(c.input_size or 0 for c in conversions)
            
            completed = [c for c in conversions if c.processing_time]
            if completed:
                behavior['avg_conversion_time'] = sum(c.processing_time for c in completed) / len(completed)
            
            # Most used formats
            for c in conversions:
                fmt = f"{c.input_format}->{c.output_format}"
                behavior['most_used_formats'][fmt] = behavior['most_used_formats'].get(fmt, 0) + 1
            
            # Last active
            behavior['last_active'] = max(c.created_at for c in conversions).isoformat()
            
            # Daily activity
            for conversion in conversions:
                day = conversion.created_at.date().isoformat()
                behavior['daily_activity'][day] = behavior['daily_activity'].get(day, 0) + 1
        
        return behavior
