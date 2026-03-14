from __future__ import with_statement

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app import create_app
from app.models import db


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


app = create_app({
    'ENABLE_BACKGROUND_TASKS': False,
    'SCHEMA_BOOTSTRAP_ENABLED': False,
    'LOG_LEVEL': 'WARNING',
})


def get_metadata():
    return db.metadata


def run_migrations_offline():
    context.configure(
        url=app.config.get('SQLALCHEMY_DATABASE_URI'),
        target_metadata=get_metadata(),
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
        url=app.config.get('SQLALCHEMY_DATABASE_URI'),
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


with app.app_context():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()