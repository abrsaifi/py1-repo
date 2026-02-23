# Cloud Storage Upload Setup Guide

This guide explains how to set up one-click cloud storage uploads for the Conversion Studio.

## Overview

The system now supports uploading converted files directly to:
- **OneDrive** (Microsoft)
- **Google Drive** (Google)
- **Dropbox** (Dropbox)

Users click a cloud storage button, authenticate once with their cloud account, and files are automatically uploaded.

## Architecture

### Frontend Flow
1. User clicks OneDrive/Google Drive/Dropbox button
2. OAuth popup opens for authentication
3. User grants permission to upload files
4. Files automatically upload to cloud account

### Backend Endpoints

**Authentication:**
- `GET /api/cloud/auth/<service>` - Initiate OAuth flow
- `GET /api/cloud/auth-callback/<service>` - Handle OAuth callback

**Upload:**
- `POST /api/cloud/upload` - Upload files to cloud storage
- `GET /api/cloud/info` - Get service configuration info

## Setup Steps

### 1. OneDrive (Microsoft)

#### Get OAuth Credentials:
1. Go to [Azure Portal](https://portal.azure.com)
2. Sign in with Microsoft account
3. Create new app registration:
   - Click "App registrations" → "New registration"
   - Name: "Conversion Studio"
   - Redirect URI: `http://localhost:5000/api/cloud/auth-callback/onedrive`
4. Save Client ID and Client Secret

#### Environment Variables:
```bash
ONEDRIVE_CLIENT_ID=your_client_id_here
ONEDRIVE_CLIENT_SECRET=your_client_secret_here
ONEDRIVE_TENANT=common
```

#### Scopes Requested:
- `Files.ReadWrite` - Upload and manage files
- `offline_access` - Access without user present

---

### 2. Google Drive

#### Get OAuth Credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: "Conversion Studio"
3. Enable "Google Drive API"
4. Create OAuth 2.0 Client ID:
   - Type: Web application
   - Authorized redirect URI: `http://localhost:5000/api/cloud/auth-callback/gdrive`
5. Download credentials JSON file

#### Environment Variables:
```bash
GDRIVE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GDRIVE_CLIENT_SECRET=your_client_secret_here
GDRIVE_API_KEY=your_api_key_here
```

#### Scopes Requested:
- `https://www.googleapis.com/auth/drive.file` - Create, modify, and upload files

---

### 3. Dropbox

#### Get OAuth Credentials:
1. Go to [Dropbox Developer Console](https://www.dropbox.com/developers)
2. Create new app:
   - Choose "Scoped access"
   - Full Dropbox access
   - Name: "Conversion Studio"
3. Set OAuth redirect URI: `http://localhost:5000/api/cloud/auth-callback/dropbox`
4. Get Client ID and Client Secret

#### Environment Variables:
```bash
DROPBOX_CLIENT_ID=your_client_id_here
DROPBOX_CLIENT_SECRET=your_client_secret_here
```

#### Permissions Needed:
- `files.content.write` - Upload files
- `files.content.read` - Read file info

---

## Configuration

### 1. Create `.env` file:
```bash
# OneDrive
ONEDRIVE_CLIENT_ID=your_onedrive_client_id
ONEDRIVE_CLIENT_SECRET=your_onedrive_secret
ONEDRIVE_TENANT=common

# Google Drive
GDRIVE_CLIENT_ID=your_gdrive_client_id
GDRIVE_CLIENT_SECRET=your_gdrive_secret
GDRIVE_API_KEY=your_api_key

# Dropbox
DROPBOX_CLIENT_ID=your_dropbox_client_id
DROPBOX_CLIENT_SECRET=your_dropbox_secret
```

### 2. Load environment variables:
```bash
# On Linux/Mac
export $(cat .env | xargs)

# On Windows PowerShell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}
```

### 3. Verify configuration:
```bash
curl http://localhost:5000/api/cloud/info
```

Should show all services configured: `"configured": true`

---

## Testing

### Manual Testing:
1. Open Conversion Studio in browser
2. Convert a file (e.g., CSV to PDF)
3. Click "OneDrive" button (or Google Drive/Dropbox)
4. Authenticate with your cloud account
5. Check your cloud storage for uploaded file

### API Testing:
```bash
# Check configuration
curl http://localhost:5000/api/cloud/info

# Check auth endpoint
curl http://localhost:5000/api/cloud/auth/onedrive

# Check upload endpoint (requires auth token)
curl -X POST http://localhost:5000/api/cloud/upload \
  -H "Content-Type: application/json" \
  -d '{"files": [], "service": "onedrive", "auth_token": "token"}'
```

---

## File Upload Limits

### OneDrive
- Maximum file size: 250 GB
- Free account: 5 GB storage
- Batch upload: Supports multiple files

### Google Drive
- Maximum file size: 5 TB
- Free account: 15 GB storage
- Batch upload: Supports multiple files

### Dropbox
- Maximum file size: 350 GB
- Free account: 2 GB storage
- Batch upload: Supports multiple files

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid service | Service name misspelled | Use: onedrive, gdrive, or dropbox |
| Missing auth token | User didn't authenticate | Click cloud button and authenticate |
| OAuth configuration missing | Credentials not set | Set environment variables |
| Upload failed | Network or storage full | Check cloud storage quota |
| Auth window blocked | Browser popup blocker | Allow popups for this site |

---

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit credentials** to version control
2. **Use environment variables** or secure vaults (AWS Secrets Manager, etc.)
3. **HTTPS only** in production
4. **Validate redirect URIs** match exactly in OAuth settings
5. **Implement token rotation** for long-running servers
6. **Log authentication events** for audit trails
7. **Sanitize file names** before upload

---

## Future Enhancements

- [ ] Batch file uploads in single request
- [ ] Progress tracking for large files
- [ ] Conflict resolution (rename/skip if exists)
- [ ] Folder organization in cloud
- [ ] Automatic cleanup of old files
- [ ] Download cloud files back to browser
- [ ] Sync converted files across multiple cloud accounts
- [ ] Integration with cloud storage webhooks

---

## Support & Troubleshooting

### Debugging:
```bash
# Check server logs
tail -f server.log | grep -i cloud

# Enable debug mode
export FLASK_DEBUG=1
python server.py
```

### Common Issues:

**1. "Invalid redirect URI"**
- Make sure redirect URI in OAuth provider **exactly matches** config
- Include protocol (http:// or https://)
- Check for trailing slashes

**2. "Invalid client ID"**
- Verify Client ID is correct (no spaces, right app)
- Check if credentials are for correct service

**3. "Permission denied"**
- User didn't grant permission
- App permissions not set in OAuth provider
- Ask user to retry and grant access

**4. "File not uploaded"**
- Check cloud storage quota
- Verify file permissions
- Check network connectivity
- Review server logs for details

---

## References

- [Microsoft Identity Platform](https://learn.microsoft.com/en-us/azure/active-directory/develop/)
- [Google Drive API Documentation](https://developers.google.com/drive)
- [Dropbox API Documentation](https://www.dropbox.com/developers)
- [OAuth 2.0 Specification](https://tools.ietf.org/html/rfc6749)
