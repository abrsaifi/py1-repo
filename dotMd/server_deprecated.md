"""
DEPRECATED: server.py

⚠️  This file is deprecated as of February 14, 2026.

The monolithic Flask application in this file has been refactored into a
modular package structure under app/. All functionality has been preserved
and moved to a more maintainable architecture.

📖 For migration details, see: MIGRATION_NOTES.md

🚀 To use the new structure:
    from app import create_app
    app = create_app()
    app.run()

📦 Or use the new entrypoint:
    python -m app.main

🐳 Or use Docker:
    docker build -t docpro:latest .
    docker run -p 5000:5000 docpro:latest

🔮 Timeline:
    - NOW (Feb 2026): New app/ package is primary; server.py kept for compatibility
    - 6 weeks: After tests pass, server.py will be marked for removal
    - 8 weeks: server.py will be removed entirely

✨ Benefits of the new structure:
    - Modular design (routes, services, utils)
    - Better testability
    - Easier to maintain and extend
    - Docker support included
    - CI/CD pipeline ready

For questions or issues, see MIGRATION_NOTES.md or DEPLOYMENT.md.
"""

import warnings
warnings.warn(
    "server.py is deprecated. Use 'from app import create_app' instead.",
    DeprecationWarning,
    stacklevel=2
)
