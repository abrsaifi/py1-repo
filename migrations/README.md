This directory is the real Alembic / Flask-Migrate migration tree.

Use:

`flask --app manage.py db current`
`flask --app manage.py db heads`
`flask --app manage.py db migrate -m "message"`
`flask --app manage.py db upgrade`

Migration commands intentionally run with warning-level logging, background tasks disabled, and schema bootstrap disabled.

The lightweight registry in `database/migrations/` remains as a human-readable tracking layer for earlier repo workflow.