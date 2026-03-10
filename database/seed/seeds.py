"""
Database Seeds
Initial data and fixtures for testing and development.
"""

SEED_DATA = {
    'users': [
        {
            'id': 'user_test_001',
            'email': 'test@example.com',
            'username': 'testuser',
            'subscription_tier': 'free'
        }
    ],
    'subscriptions': [
        {
            'user_id': 'user_test_001',
            'tier': 'free',
            'monthly_limit': 10,
            'is_active': True
        }
    ],
    'file_formats': [
        {'format': 'pdf',  'category': 'document'},
        {'format': 'docx', 'category': 'document'},
        {'format': 'xlsx', 'category': 'spreadsheet'},
        {'format': 'png',  'category': 'image'},
        {'format': 'jpg',  'category': 'image'},
    ]
}


def seed_database(db_connection):
    """
    Seed database with initial data
    
    Args:
        db_connection: Database connection object
    """
    # TODO: Implement database seeding logic
    pass


if __name__ == '__main__':
    print("Database Seeds Module")
    print("Use this to initialize test data")
    for table, data in SEED_DATA.items():
        print(f"  {table}: {len(data)} records")
