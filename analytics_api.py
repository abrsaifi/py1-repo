"""
Analytics API Module
Provides endpoints for Phase 12 Advanced Analytics features
"""

from flask import jsonify, request
from datetime import datetime, timedelta
import uuid
import json
from functools import wraps

# Mock data storage (would be database in production)
analytics_reports = {}
analytics_metrics_db = {}

# Response wrapper
def api_response(success=True, data=None, error=None, message=None, status_code=200):
    """Standardized API response format"""
    response = {
        "success": success,
        "meta": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": str(uuid.uuid4())[:8]
        }
    }
    
    if data is not None:
        response["data"] = data
    if error is not None:
        response["error"] = error
    if message is not None:
        response["message"] = message
        
    return jsonify(response), status_code

def register_analytics_api(app):
    """Register all analytics API endpoints"""
    
    # =========== ANALYTICS DASHBOARD ===========
    @app.route('/api/analytics/dashboard', methods=['GET'])
    def get_analytics_dashboard():
        """Get analytics dashboard data with KPIs and insights"""
        dashboard_data = {
            "kpis": {
                "total_revenue": {
                    "value": 245600.50,
                    "change": 12.5,
                    "trend": "up",
                    "currency": "USD"
                },
                "units_sold": {
                    "value": 8450,
                    "change": 8.3,
                    "trend": "up"
                },
                "avg_price": {
                    "value": 29.05,
                    "change": -2.1,
                    "trend": "down",
                    "currency": "USD"
                },
                "active_users": {
                    "value": 1245,
                    "change": 15.7,
                    "trend": "up"
                }
            },
            "insights": [
                {
                    "id": "1",
                    "title": "Strong Q1 Performance",
                    "description": "Revenue is up 12.5% compared to last quarter",
                    "severity": "positive",
                    "actionable": True
                },
                {
                    "id": "2",
                    "title": "Price Optimization Opportunity",
                    "description": "Average price down 2.1% - consider dynamic pricing",
                    "severity": "warning",
                    "actionable": True
                },
                {
                    "id": "3",
                    "title": "User Growth Accelerating",
                    "description": "Active users up 15.7% - highest growth rate this year",
                    "severity": "positive",
                    "actionable": False
                }
            ],
            "recent_metrics": [
                {"date": "2026-03-05", "revenue": 8450.50, "users": 145, "conversion": 3.2},
                {"date": "2026-03-04", "revenue": 7820.25, "users": 138, "conversion": 3.1},
                {"date": "2026-03-03", "revenue": 9120.75, "users": 152, "conversion": 3.4},
            ]
        }
        
        return api_response(data=dashboard_data)
    
    # =========== STATISTICS ANALYSIS ===========
    @app.route('/api/analytics/statistics', methods=['POST'])
    def get_statistics():
        """Get comprehensive statistical analysis of a dataset"""
        data = request.get_json()
        dataset = data.get('dataset', 'sales')  # sales, traffic, users, performance
        
        # Generate mock statistics based on dataset
        statistics = {
            "descriptive": {
                "mean": 125.45,
                "median": 118.20,
                "mode": 115.00,
                "std_dev": 28.50,
                "variance": 812.25,
                "min": 45.00,
                "max": 285.50,
                "q1": 95.00,
                "q3": 155.00,
                "range": 240.50,
                "iqr": 60.00
            },
            "distribution": {
                "skewness": 0.45,
                "kurtosis": -0.35,
                "normality": {
                    "test": "Shapiro-Wilk",
                    "p_value": 0.087,
                    "is_normal": True
                }
            },
            "inferential": {
                "confidence_interval_95": [112.50, 138.40],
                "t_statistic": 2.45,
                "p_value": 0.021,
                "significant": True
            },
            "correlation": {
                "variables": ["Revenue", "Marketing Spend", "User Count"],
                "matrix": [
                    [1.00, 0.78, 0.65],
                    [0.78, 1.00, 0.52],
                    [0.65, 0.52, 1.00]
                ],
                "significant_pairs": [
                    {"var1": "Revenue", "var2": "Marketing Spend", "r": 0.78, "p": 0.001}
                ]
            },
            "regression": {
                "model": "Linear",
                "r_squared": 0.612,
                "coefficients": {
                    "intercept": 45.20,
                    "marketing_spend": 0.85,
                    "user_count": 0.12
                },
                "model_fit": "Good"
            }
        }
        
        return api_response(data=statistics)
    
    # =========== FORECASTING ===========
    @app.route('/api/analytics/forecast', methods=['POST'])
    def get_forecast():
        """Get predictive analytics with forecasting"""
        data = request.get_json()
        metric = data.get('metric', 'revenue')
        days = data.get('days_ahead', 14)
        
        # Generate forecast data
        forecast = {
            "metric": metric,
            "forecast_days": days,
            "model": {
                "name": "ARIMA",
                "accuracy": 0.92,
                "mae": 125.50,
                "rmse": 185.75
            },
            "forecast_values": [
                {"day": i, "forecast": 8450 + (i * 85), "lower_ci": 8200 + (i * 80), "upper_ci": 8700 + (i * 90)}
                for i in range(1, min(days + 1, 15))
            ],
            "anomalies": [
                {
                    "day": 3,
                    "value": 7200,
                    "expected": 8450,
                    "severity": "critical",
                    "type": "drop",
                    "sigma": 2.8
                },
                {
                    "day": 7,
                    "value": 9800,
                    "expected": 8620,
                    "severity": "warning",
                    "type": "spike",
                    "sigma": 1.9
                }
            ],
            "trends": {
                "direction": "uptrend",
                "slope": 85.5,
                "seasonality": "weekly",
                "volatility": "moderate"
            },
            "recommendations": [
                "Increase marketing spend - uptrend suggests strong market demand",
                "Address day 3 anomaly - investigate external factors",
                "Prepare inventory for forecasted peak on day 12",
                "Monitor seasonal pattern for Q2 planning"
            ]
        }
        
        return api_response(data=forecast)
    
    # =========== VISUALIZATION DATA ===========
    @app.route('/api/analytics/heatmap', methods=['GET'])
    def get_heatmap_data():
        """Get heatmap data for 7-day × 24-hour activity grid"""
        import random
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = list(range(24))
        
        heatmap = {
            "days": days,
            "hours": hours,
            "data": [
                [random.randint(10, 100) for _ in hours]
                for _ in days
            ],
            "scale": {
                "min": 0,
                "max": 100,
                "unit": "activity_count"
            }
        }
        
        return api_response(data=heatmap)
    
    @app.route('/api/analytics/scatter', methods=['GET'])
    def get_scatter_data():
        """Get scatter plot data for correlation analysis"""
        import random
        
        scatter = {
            "x_label": "Marketing Spend ($1000s)",
            "y_label": "Revenue ($1000s)",
            "correlation": 0.78,
            "r_squared": 0.612,
            "points": [
                {"x": random.uniform(5, 50), "y": random.uniform(20, 80)}
                for _ in range(50)
            ],
            "trend_line": {
                "slope": 1.2,
                "intercept": 15.5,
                "equation": "y = 1.2x + 15.5"
            }
        }
        
        return api_response(data=scatter)
    
    @app.route('/api/analytics/treemap', methods=['GET'])
    def get_treemap_data():
        """Get treemap data for product category hierarchy"""
        treemap = {
            "name": "Product Revenue",
            "children": [
                {
                    "name": "Electronics",
                    "value": 85000,
                    "children": [
                        {"name": "Tablets", "value": 35000},
                        {"name": "Smartphones", "value": 45000},
                        {"name": "Accessories", "value": 5000}
                    ]
                },
                {
                    "name": "Clothing",
                    "value": 62000,
                    "children": [
                        {"name": "Men's", "value": 30000},
                        {"name": "Women's", "value": 25000},
                        {"name": "Kids", "value": 7000}
                    ]
                },
                {
                    "name": "Home & Garden",
                    "value": 48000,
                    "children": [
                        {"name": "Furniture", "value": 25000},
                        {"name": "Decor", "value": 15000},
                        {"name": "Tools", "value": 8000}
                    ]
                }
            ]
        }
        
        return api_response(data=treemap)
    
    @app.route('/api/analytics/sankey', methods=['GET'])
    def get_sankey_data():
        """Get sankey diagram data for customer journey"""
        sankey = {
            "nodes": [
                {"name": "Awareness"},
                {"name": "Consideration"},
                {"name": "Evaluation"},
                {"name": "Purchase"},
                {"name": "Loyalty"}
            ],
            "links": [
                {"source": 0, "target": 1, "value": 100000},
                {"source": 1, "target": 2, "value": 75000},
                {"source": 2, "target": 3, "value": 45000},
                {"source": 3, "target": 4, "value": 35000},
                {"source": 1, "target": 3, "value": 8000},  # Direct conversion
            ]
        }
        
        return api_response(data=sankey)
    
    @app.route('/api/analytics/funnel', methods=['GET'])
    def get_funnel_data():
        """Get funnel chart data for conversion stages"""
        funnel = {
            "stages": [
                {"name": "Visits", "value": 100000},
                {"name": "Product Views", "value": 65000},
                {"name": "Add to Cart", "value": 28000},
                {"name": "Start Checkout", "value": 18000},
                {"name": "Enter Payment", "value": 14000},
                {"name": "Complete Order", "value": 12000},
                {"name": "Confirm Email", "value": 10000}
            ],
            "conversion_rates": [
                0.65, 0.43, 0.64, 0.78, 0.86, 0.83
            ],
            "dropoff_analysis": {
                "biggest_drop": "Product Views → Add to Cart (56.9%)",
                "optimization_focus": "Reduce friction in add-to-cart process"
            }
        }
        
        return api_response(data=funnel)
    
    @app.route('/api/analytics/radar', methods=['GET'])
    def get_radar_data():
        """Get radar chart data for product comparison"""
        radar = {
            "categories": ["Quality", "Popularity", "Demand", "Profitability"],
            "products": [
                {
                    "name": "Product A",
                    "values": [9, 7, 8, 6],
                    "color": "rgba(54, 162, 235, 0.5)"
                },
                {
                    "name": "Product B",
                    "values": [7, 9, 6, 8],
                    "color": "rgba(255, 99, 132, 0.5)"
                },
                {
                    "name": "Product C",
                    "values": [8, 6, 9, 7],
                    "color": "rgba(75, 192, 75, 0.5)"
                }
            ]
        }
        
        return api_response(data=radar)
    
    # =========== REPORTS MANAGEMENT ===========
    @app.route('/api/reports', methods=['GET'])
    def list_reports():
        """List all custom reports"""
        reports = [
            {
                "id": "report-1",
                "name": "Monthly Sales Report",
                "metrics": ["revenue", "units_sold"],
                "dimensions": ["product_category", "region"],
                "created": "2026-03-01",
                "modified": "2026-03-04"
            },
            {
                "id": "report-2",
                "name": "User Growth Analysis",
                "metrics": ["active_users", "new_signups"],
                "dimensions": ["user_segment", "temporal"],
                "created": "2026-02-15",
                "modified": "2026-03-03"
            }
        ]
        
        return api_response(data=reports)
    
    @app.route('/api/reports', methods=['POST'])
    def create_report():
        """Create a new custom report"""
        data = request.get_json()
        report_id = str(uuid.uuid4())
        
        new_report = {
            "id": report_id,
            "name": data.get('name'),
            "metrics": data.get('metrics', []),
            "dimensions": data.get('dimensions', []),
            "filters": data.get('filters', {}),
            "created": datetime.utcnow().isoformat(),
            "modified": datetime.utcnow().isoformat()
        }
        
        analytics_reports[report_id] = new_report
        return api_response(data=new_report, status_code=201)
    
    @app.route('/api/reports/<report_id>', methods=['GET'])
    def get_report(report_id):
        """Get a specific report"""
        report = analytics_reports.get(report_id)
        if not report:
            return api_response(success=False, error={"code": "NOT_FOUND"}, status_code=404)
        return api_response(data=report)
    
    @app.route('/api/reports/<report_id>', methods=['PUT'])
    def update_report(report_id):
        """Update an existing report"""
        if report_id not in analytics_reports:
            return api_response(success=False, error={"code": "NOT_FOUND"}, status_code=404)
        
        data = request.get_json()
        analytics_reports[report_id].update({**data, "modified": datetime.utcnow().isoformat()})
        
        return api_response(data=analytics_reports[report_id])
    
    @app.route('/api/reports/<report_id>', methods=['DELETE'])
    def delete_report(report_id):
        """Delete a report"""
        if report_id not in analytics_reports:
            return api_response(success=False, error={"code": "NOT_FOUND"}, status_code=404)
        
        del analytics_reports[report_id]
        return api_response(data={"message": "Report deleted"})
    
    @app.route('/api/reports/<report_id>/export', methods=['POST'])
    def export_report(report_id):
        """Export report in specified format"""
        if report_id not in analytics_reports:
            return api_response(success=False, error={"code": "NOT_FOUND"}, status_code=404)
        
        data = request.get_json()
        format_type = data.get('format', 'pdf')  # pdf, excel, csv
        
        return api_response(data={
            "export_url": f"/downloads/report_{report_id}.{format_type}",
            "format": format_type,
            "generated_at": datetime.utcnow().isoformat()
        })


# Export function for use in main server.py
def init_analytics_api(app):
    """Initialize analytics API endpoints"""
    register_analytics_api(app)
