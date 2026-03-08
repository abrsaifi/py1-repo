"""
Analytics Service Blueprints
Import all blueprints for registration in main.py
"""

from .metrics_bp import metrics_bp
from .dashboards_bp import dashboards_bp
from .reports_bp import reports_bp
from .alerts_bp import alerts_bp
from .custom_metrics_bp import custom_metrics_bp
from .queries_bp import queries_bp
from .export_bp import export_bp

__all__ = [
    'metrics_bp',
    'dashboards_bp',
    'reports_bp',
    'alerts_bp',
    'custom_metrics_bp',
    'queries_bp',
    'export_bp',
]
