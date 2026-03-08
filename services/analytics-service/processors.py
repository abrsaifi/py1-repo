"""
Metrics Processors
Handles calculation, aggregation, and persistence of analytics metrics
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from analytics_models import (
    SystemMetric, ServiceMetric, UserActivityMetric, BusinessMetric,
    AggregationLevel, MetricType
)
from decimal import Decimal
from collections import defaultdict

logger = logging.getLogger(__name__)


class MetricsProcessor:
    """Base metrics processor class"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def calculate_percentiles(self, values: list, percentiles=[0.5, 0.95, 0.99]):
        """Calculate percentile values from data points"""
        if not values:
            return {p: 0 for p in percentiles}
        
        sorted_values = sorted(values)
        result = {}
        
        for p in percentiles:
            index = int(len(sorted_values) * p)
            result[p] = sorted_values[min(index, len(sorted_values) - 1)]
        
        return result
    
    def aggregate_values(self, values: list, method: str = 'avg'):
        """Aggregate values using specified method"""
        if not values:
            return 0
        
        if method == 'sum':
            return sum(values)
        elif method == 'avg':
            return sum(values) / len(values)
        elif method == 'min':
            return min(values)
        elif method == 'max':
            return max(values)
        elif method == 'count':
            return len(values)
        else:
            return sum(values) / len(values)


class SystemMetricProcessor(MetricsProcessor):
    """Process and aggregate system-wide metrics"""
    
    def process_metrics(self, tenant_id: str, raw_metrics: dict):
        """
        Process raw metrics and create SystemMetric records
        
        Args:
            tenant_id: Tenant identifier
            raw_metrics: Dictionary with metric data
                {
                    'service_name': 'auth-service',
                    'metric_name': 'cpu_usage',
                    'metric_type': 'gauge',
                    'values': [45.2, 46.1, 45.8]  # Multiple measurements
                }
        """
        try:
            service = raw_metrics.get('service_name', 'unknown')
            metric_name = raw_metrics.get('metric_name', 'unknown')
            metric_type = raw_metrics.get('metric_type', 'gauge')
            values = raw_metrics.get('values', [])
            
            now = datetime.utcnow()
            
            # Calculate aggregations for different time periods
            for aggregation_level in ['minute', 'hour', 'day']:
                if aggregation_level == 'minute':
                    period_start = now - timedelta(minutes=1)
                elif aggregation_level == 'hour':
                    period_start = now - timedelta(hours=1)
                else:
                    period_start = now - timedelta(days=1)
                
                # Calculate percentiles
                percentiles = self.calculate_percentiles(values)
                
                metric = SystemMetric(
                    tenant_id=tenant_id,
                    service_name=service,
                    metric_name=metric_name,
                    metric_type=metric_type,
                    aggregation_level=aggregation_level,
                    timestamp=now,
                    period_start=period_start,
                    period_end=now,
                    value=self.aggregate_values(values, 'avg'),
                    min_value=self.aggregate_values(values, 'min'),
                    max_value=self.aggregate_values(values, 'max'),
                    avg_value=self.aggregate_values(values, 'avg'),
                    p50_value=percentiles.get(0.5, 0),
                    p95_value=percentiles.get(0.95, 0),
                    p99_value=percentiles.get(0.99, 0),
                    count=len(values),
                )
                
                self.session.add(metric)
            
            self.session.commit()
            logger.info(f"Processed system metric: {service}/{metric_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error processing system metrics: {e}")
            self.session.rollback()
            return False


class ServiceMetricProcessor(MetricsProcessor):
    """Process service-level performance metrics"""
    
    def process_service_metrics(self, tenant_id: str, service_name: str, raw_data: dict):
        """
        Process service performance metrics
        
        Args:
            tenant_id: Tenant identifier
            service_name: Name of the service
            raw_data: Service metrics data
                {
                    'response_times': [100, 120, 95, 150],  # milliseconds
                    'request_count': 1000,
                    'successful_requests': 998,
                    'failed_requests': 2,
                    'cpu_usage': 45.2,
                    'memory_usage': 62.5,
                    'disk_usage': 78.3,
                    'uptime_percent': 99.95
                }
        """
        try:
            response_times = raw_data.get('response_times', [])
            request_count = raw_data.get('request_count', 0)
            successful = raw_data.get('successful_requests', 0)
            failed = raw_data.get('failed_requests', 0)
            
            # Calculate latency percentiles
            percentiles = self.calculate_percentiles(response_times)
            
            # Calculate error rates
            error_rate = (failed / request_count * 100) if request_count > 0 else 0
            
            now = datetime.utcnow()
            period_start = now - timedelta(hours=1)
            
            metric = ServiceMetric(
                tenant_id=tenant_id,
                service_name=service_name,
                period_start=period_start,
                period_end=now,
                response_time_p50=percentiles.get(0.5, 0),
                response_time_p95=percentiles.get(0.95, 0),
                response_time_p99=percentiles.get(0.99, 0),
                response_time_avg=self.aggregate_values(response_times, 'avg'),
                total_requests=request_count,
                successful_requests=successful,
                failed_requests=failed,
                error_rate=error_rate,
                error_count_4xx=raw_data.get('error_4xx', 0),
                error_count_5xx=raw_data.get('error_5xx', 0),
                timeout_count=raw_data.get('timeout_count', 0),
                cpu_usage_percent=raw_data.get('cpu_usage', 0),
                memory_usage_percent=raw_data.get('memory_usage', 0),
                disk_usage_percent=raw_data.get('disk_usage', 0),
                uptime_percent=raw_data.get('uptime_percent', 100),
            )
            
            self.session.add(metric)
            self.session.commit()
            
            logger.info(f"Processed service metrics for {service_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error processing service metrics: {e}")
            self.session.rollback()
            return False


class UserActivityMetricProcessor(MetricsProcessor):
    """Process user activity and engagement metrics"""
    
    def process_activity_metrics(self, tenant_id: str, period_data: dict):
        """
        Process user activity metrics
        
        Args:
            tenant_id: Tenant identifier
            period_data: Activity metrics data
                {
                    'period_start': '2024-01-01',
                    'total_users': 5000,
                    'active_users_24h': 2500,
                    'new_users': 150,
                    'churned_users': 45,
                    'sessions': 5000,
                    'avg_session_duration': 480,  # seconds
                    'dau': 2500,
                    'wau': 4200,
                    'mau': 4800,
                    'top_features': [
                        {'feature': 'dashboard', 'usage_count': 1200},
                        {'feature': 'export', 'usage_count': 800}
                    ],
                    'device_metrics': {
                        'iOS': 1200,
                        'Android': 800,
                        'Web': 500
                    }
                }
        """
        try:
            dau = period_data.get('dau', 0)
            wau = period_data.get('wau', 0)
            mau = period_data.get('mau', 0)
            
            # Calculate engagement ratios
            dau_wau_ratio = (dau / wau * 100) if wau > 0 else 0
            dau_mau_ratio = (dau / mau * 100) if mau > 0 else 0
            
            # Process feature usage
            top_features = []
            for feature_data in period_data.get('top_features', []):
                top_features.append({
                    'feature_name': feature_data.get('feature'),
                    'usage_count': feature_data.get('usage_count')
                })
            
            # Process device metrics
            device_metrics = period_data.get('device_metrics', {})
            
            now = datetime.utcnow()
            period_start = datetime.fromisoformat(period_data.get('period_start', now.isoformat()))
            
            metric = UserActivityMetric(
                tenant_id=tenant_id,
                period_start=period_start,
                period_end=now,
                total_users=period_data.get('total_users', 0),
                active_users=period_data.get('active_users_24h', 0),
                new_users=period_data.get('new_users', 0),
                churned_users=period_data.get('churned_users', 0),
                total_sessions=period_data.get('sessions', 0),
                avg_session_duration=period_data.get('avg_session_duration', 0),
                bounce_rate=period_data.get('bounce_rate', 0),
                dau=dau,
                wau=wau,
                mau=mau,
                dau_wau_ratio=dau_wau_ratio,
                dau_mau_ratio=dau_mau_ratio,
                top_features=top_features,
                top_devices=device_metrics,
            )
            
            self.session.add(metric)
            self.session.commit()
            
            logger.info(f"Processed activity metrics for tenant {tenant_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error processing activity metrics: {e}")
            self.session.rollback()
            return False


class BusinessMetricProcessor(MetricsProcessor):
    """Process business KPI metrics"""
    
    def process_business_metrics(self, tenant_id: str, financial_data: dict):
        """
        Process business KPI metrics
        
        Args:
            tenant_id: Tenant identifier
            financial_data: Business metrics data
                {
                    'period_start': '2024-01-01',
                    'total_revenue': 50000,
                    'mrr': 50000,
                    'arr': 600000,
                    'recurring_revenue': 45000,
                    'new_customers': 20,
                    'churned_customers': 3,
                    'total_customers': 250,
                    'trial_conversions': 15,
                    'churn_rate': 1.2,
                    'ltv': 10000,
                    'cac': 500,
                    'growth_rate': 12.5,
                    'expansion_revenue': 5000,
                    'contraction_revenue': -2000,
                    'nrr': 110.5
                }
        """
        try:
            # Extract data
            mrr = Decimal(str(financial_data.get('mrr', 0)))
            arr = Decimal(str(financial_data.get('arr', 0)))
            ltv = Decimal(str(financial_data.get('ltv', 0)))
            cac = Decimal(str(financial_data.get('cac', 0)))
            
            # Calculate ratios
            ltv_cac_ratio = float(ltv / cac) if cac > 0 else 0
            
            # Calculate retention from churn
            churn_rate = float(financial_data.get('churn_rate', 0))
            retention_rate = 100 - churn_rate
            
            now = datetime.utcnow()
            period_start = datetime.fromisoformat(financial_data.get('period_start', now.isoformat()))
            
            metric = BusinessMetric(
                tenant_id=tenant_id,
                period_start=period_start,
                period_end=now,
                total_revenue=Decimal(str(financial_data.get('total_revenue', 0))),
                recurring_revenue=Decimal(str(financial_data.get('recurring_revenue', 0))),
                mrr=mrr,
                arr=arr,
                average_order_value=Decimal(str(financial_data.get('aov', 0))),
                revenue_per_user=Decimal(str(financial_data.get('revenue_per_user', 0))),
                conversion_rate=float(financial_data.get('conversion_rate', 0)),
                trial_to_paid_rate=float(financial_data.get('trial_conversions', 0)) / 100,
                total_customers=financial_data.get('total_customers', 0),
                new_customers=financial_data.get('new_customers', 0),
                churned_customers=financial_data.get('churned_customers', 0),
                customer_lifetime_value=ltv,
                customer_acquisition_cost=cac,
                ltv_cac_ratio=Decimal(str(ltv_cac_ratio)),
                churn_rate=Decimal(str(churn_rate)),
                retention_rate=Decimal(str(retention_rate)),
                month_over_month_growth=Decimal(str(financial_data.get('growth_rate', 0))),
                expansion_revenue=Decimal(str(financial_data.get('expansion_revenue', 0))),
                contraction_revenue=Decimal(str(financial_data.get('contraction_revenue', 0))),
                net_revenue_retention=Decimal(str(financial_data.get('nrr', 100))),
                product_adoption_rate=float(financial_data.get('adoption_rate', 0)),
            )
            
            self.session.add(metric)
            self.session.commit()
            
            logger.info(f"Processed business metrics for tenant {tenant_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error processing business metrics: {e}")
            self.session.rollback()
            return False


class MetricsAggregator:
    """Aggregates metrics across time periods (rollup operations)"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def rollup_minutely_to_hourly(self, tenant_id: str, service_name: str):
        """
        Aggregate minutely metrics to hourly
        """
        try:
            now = datetime.utcnow()
            hour_ago = now - timedelta(hours=1)
            
            # Query minutely metrics
            minutely_metrics = self.session.query(SystemMetric).filter(
                SystemMetric.tenant_id == tenant_id,
                SystemMetric.service_name == service_name,
                SystemMetric.aggregation_level == 'minute',
                SystemMetric.timestamp.between(hour_ago, now)
            ).all()
            
            if not minutely_metrics:
                return 0
            
            # Group by metric_name
            grouped = defaultdict(list)
            for m in minutely_metrics:
                grouped[m.metric_name].append(m.value)
            
            # Create hourly aggregations
            created = 0
            for metric_name, values in grouped.items():
                hourly = SystemMetric(
                    tenant_id=tenant_id,
                    service_name=service_name,
                    metric_name=metric_name,
                    aggregation_level='hour',
                    timestamp=now,
                    period_start=hour_ago,
                    period_end=now,
                    value=sum(values) / len(values),
                    min_value=min(values),
                    max_value=max(values),
                    count=len(values),
                )
                self.session.add(hourly)
                created += 1
            
            self.session.commit()
            logger.info(f"Rolled up {created} hourly metrics from minutely data")
            return created
        
        except Exception as e:
            logger.error(f"Error rolling up metrics: {e}")
            self.session.rollback()
            return 0
    
    def cleanup_old_metrics(self, tenant_id: str, aggregation_level: str, retention_days: int):
        """
        Remove old metrics based on retention policy
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            deleted = self.session.query(SystemMetric).filter(
                SystemMetric.tenant_id == tenant_id,
                SystemMetric.aggregation_level == aggregation_level,
                SystemMetric.timestamp < cutoff_date
            ).delete()
            
            self.session.commit()
            logger.info(f"Cleaned up {deleted} old metrics for {aggregation_level} level")
            return deleted
        
        except Exception as e:
            logger.error(f"Error cleaning up metrics: {e}")
            self.session.rollback()
            return 0
