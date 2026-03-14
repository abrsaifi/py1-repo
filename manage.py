"""Migration command entrypoint for Flask CLI and Flask-Migrate."""
from app import create_app
from app.models import db


app = create_app({
    'ENABLE_BACKGROUND_TASKS': False,
    'SCHEMA_BOOTSTRAP_ENABLED': False,
    'LOG_LEVEL': 'WARNING',
})


@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db': db}


if __name__ == '__main__':
    app.run()
