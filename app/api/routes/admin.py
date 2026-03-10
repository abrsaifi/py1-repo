"""Admin API routes for system management."""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import db, User, Conversion, Subscription, APIKey
from app.middleware.auth import admin_required

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

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
    
    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page,
        'users': [user.to_dict() for user in pagination.items]
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
        'user': user.to_dict()
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
    data = request.get_json()
    
    if 'new_password' not in data:
        return jsonify({'error': 'new_password required'}), 400
    
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'}), 200

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
    start_date = datetime.utcnow() - timedelta(days=days)
    
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
# ROLE MANAGEMENT
# ============================================================================

@bp.route('/roles', methods=['GET'])
@admin_required
def get_roles():
    """Get available roles and their permissions."""
    roles = {
        'user': {
            'name': 'User',
            'description': 'Regular user with conversion capabilities',
            'permissions': [
                'conversions:read',
                'conversions:write',
                'profile:read',
                'profile:write'
            ]
        },
        'admin': {
            'name': 'Administrator',
            'description': 'Full system access',
            'permissions': [
                '*'
            ]
        },
        'moderator': {
            'name': 'Moderator',
            'description': 'User support and moderation',
            'permissions': [
                'users:read',
                'users:support',
                'conversions:read'
            ]
        }
    }
    
    return jsonify(roles), 200

# ============================================================================
# SYSTEM HEALTH
# ============================================================================

@bp.route('/health', methods=['GET'])
@admin_required
def get_system_health():
    """Get system health status."""
    try:
        # Database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    # Coming soon: worker status, cache status, etc.
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'components': {
            'database': db_status,
            'api': 'healthy',
            'workers': 'not_configured'  # To be implemented
        },
        'timestamp': datetime.utcnow().isoformat()
    }), 200
