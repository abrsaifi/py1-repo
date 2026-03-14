import os

from . import create_app

app = create_app()


if __name__ == '__main__':
    # Avoid the Werkzeug reloader here because it initializes the app twice,
    # which duplicates startup side effects like background maintenance tasks.
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes', 'on'}
    app.run(host=host, port=port, debug=debug, use_reloader=False)
