"""Database seeds for development and local verification."""

SEED_DATA = {
    'users': [
        {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'ChangeMe123!',
            'plan': 'free',
            'quota_gb': 5,
            'is_active': True,
            'is_verified': True,
        }
    ],
    'subscriptions': [
        {
            'user_email': 'test@example.com',
            'plan': 'free',
            'storage_quota_gb': 5,
            'monthly_conversion_limit': 10,
            'max_file_size_mb': 50,
            'price_per_month': 0.0,
            'is_active': True,
        }
    ],
    'file_formats': [
        {'format': 'pdf', 'category': 'document'},
        {'format': 'docx', 'category': 'document'},
        {'format': 'xlsx', 'category': 'spreadsheet'},
        {'format': 'png', 'category': 'image'},
        {'format': 'jpg', 'category': 'image'},
    ]
}


def _resolve_session(db_connection):
    if hasattr(db_connection, 'session'):
        return db_connection.session
    if all(hasattr(db_connection, attr) for attr in ('add', 'commit', 'query')):
        return db_connection
    raise TypeError('seed_database expects a Flask-SQLAlchemy db object or SQLAlchemy session')


def seed_database(db_connection):
    """Seed the current database with a small development baseline."""
    from app.models import Subscription, User

    session = _resolve_session(db_connection)
    summary = {
        'users_created': 0,
        'users_updated': 0,
        'subscriptions_created': 0,
        'subscriptions_updated': 0,
        'file_formats_loaded': len(SEED_DATA['file_formats']),
    }

    users_by_email = {}
    for payload in SEED_DATA['users']:
        user = session.query(User).filter_by(email=payload['email']).first()
        created = user is None
        if created:
            user = User(email=payload['email'], username=payload['username'])
            session.add(user)

        user.username = payload['username']
        user.plan = payload.get('plan', user.plan)
        user.quota_gb = payload.get('quota_gb', user.quota_gb)
        user.is_active = payload.get('is_active', user.is_active)
        user.is_verified = payload.get('is_verified', user.is_verified)
        if payload.get('password'):
            user.set_password(payload['password'])

        users_by_email[user.email] = user
        summary['users_created' if created else 'users_updated'] += 1

    session.flush()

    for payload in SEED_DATA['subscriptions']:
        user = users_by_email.get(payload['user_email'])
        if user is None:
            user = session.query(User).filter_by(email=payload['user_email']).first()
        if user is None:
            raise ValueError(f"Cannot seed subscription for missing user: {payload['user_email']}")

        subscription = session.query(Subscription).filter_by(user_id=user.id).first()
        created = subscription is None
        if created:
            subscription = Subscription(user_id=user.id)
            session.add(subscription)

        subscription.plan = payload.get('plan', subscription.plan)
        subscription.storage_quota_gb = payload.get('storage_quota_gb', subscription.storage_quota_gb)
        subscription.monthly_conversion_limit = payload.get('monthly_conversion_limit', subscription.monthly_conversion_limit)
        subscription.max_file_size_mb = payload.get('max_file_size_mb', subscription.max_file_size_mb)
        subscription.price_per_month = payload.get('price_per_month', subscription.price_per_month)
        subscription.is_active = payload.get('is_active', subscription.is_active)

        summary['subscriptions_created' if created else 'subscriptions_updated'] += 1

    session.commit()
    return summary


if __name__ == '__main__':
    print("Database Seeds Module")
    print("Use this to initialize test data")
    for table, data in SEED_DATA.items():
        print(f"  {table}: {len(data)} records")
