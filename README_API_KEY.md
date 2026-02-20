Enabling and using the upload API key

This project supports an optional API key to gate upload/convert endpoints. Follow these steps to enable and use it:

1) Set the API key in server configuration

- In development, add the following before starting the Flask app (for example in `server.py` or the start script):

    app.config['UPLOAD_API_KEY'] = 'your-secret-key'

- In production, set an environment variable and load it in configuration. Example (PowerShell):

    $env:UPLOAD_API_KEY = 'your-secret-key'

2) How the frontend sends the key

- The page includes a small UI "Set API Key" button in the navigation. Clicking it opens a prompt where you can paste the API key. The key is stored in `sessionStorage` for the current browser tab.
- The client code prefers the `sessionStorage` key (set by the prompt) and falls back to the server-injected meta tag `upload-api-key` when present.
- All chunk uploads and assembled conversion requests include the `X-API-Key` header automatically when a key is set in the browser session.

3) Example curl usage

To call the `convert-uploaded` endpoint from a script, include the header:

    curl -H "X-API-Key: your-secret-key" -H "Content-Type: application/json" -d '{"uploads": [{"upload_id":"...","filename":"..."}], "target_format":"png"}' http://localhost:5000/convert-uploaded

4) Notes and security

- The browser prompt stores the key only in `sessionStorage` (not persisted across browser restarts). This is a convenience for local testing and demos. For production, avoid embedding static keys into client HTML. Use a proper authentication flow.
- The server rejects requests without the correct `X-API-Key` when `app.config['UPLOAD_API_KEY']` is set.
- Consider using stronger auth (OAuth, JWT) and transport security (HTTPS) for production deployments.

If you want, I can add a small server-side snippet to load `UPLOAD_API_KEY` from an environment variable automatically on startup and a short README section with recommended production practices.
