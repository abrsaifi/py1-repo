"""
Collaboration API Module
Provides endpoints for Phase 13 Collaboration features
"""

from flask import jsonify, request
from datetime import datetime
import uuid
import json

# Mock data storage (would be database in production)
documents_db = {}
shares_db = {}
comments_db = {}
teams_db = {}
team_members_db = {}
access_logs = []
notifications_db = {}

def api_response(success=True, data=None, error=None, message=None, status_code=200):
    """Standardized API response format"""
    response = {
        "success": success,
        "meta": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": str(uuid.uuid4())[:8]
        }
    }
    
    if data is not None:
        response["data"] = data
    if error is not None:
        response["error"] = error
    if message is not None:
        response["message"] = message
        
    return jsonify(response), status_code

def log_access(action, resource_id, resource_type, user_id=None):
    """Log access for audit trail"""
    access_logs.append({
        "id": str(uuid.uuid4()),
        "action": action,
        "resource_id": resource_id,
        "resource_type": resource_type,
        "user_id": user_id or "anonymous",
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": request.remote_addr
    })

def register_collaboration_api(app):
    """Register all collaboration API endpoints"""
    
    # =========== COLLABORATION DASHBOARD ===========
    @app.route('/api/collaboration/dashboard', methods=['GET'])
    def get_collaboration_dashboard():
        """Get collaboration dashboard data"""
        dashboard = {
            "stats": {
                "shared_items": 24,
                "team_members": 42,
                "activities": 156,
                "pending_requests": 3
            },
            "recent_activities": [
                {
                    "id": "1",
                    "type": "document_shared",
                    "user": "John Doe",
                    "resource": "Q1 Report.pdf",
                    "timestamp": "2026-03-05 10:30:00",
                    "details": "Shared with Marketing Team"
                },
                {
                    "id": "2",
                    "type": "comment_added",
                    "user": "Jane Smith",
                    "resource": "Budget Planning.xlsx",
                    "timestamp": "2026-03-05 09:15:00",
                    "details": "Added comment: Need revision"
                },
                {
                    "id": "3",
                    "type": "team_created",
                    "user": "Admin",
                    "resource": "Product Team",
                    "timestamp": "2026-03-04 14:45:00",
                    "details": "New team created"
                }
            ],
            "pending_approvals": [
                {
                    "id": "1",
                    "type": "access_request",
                    "user": "Bob Wilson",
                    "resource": "Financial Data.xlsx",
                    "requested_at": "2026-03-04 16:20:00"
                }
            ]
        }
        
        log_access("view", "dashboard", "collaboration")
        return api_response(data=dashboard)
    
    # =========== DOCUMENT SHARING ===========
    @app.route('/api/documents', methods=['GET'])
    def list_documents():
        """List all documents for current user"""
        documents = [
            {
                "id": "doc-1",
                "name": "Q1 Report.pdf",
                "owner": "John Doe",
                "file_size": 2458624,
                "mime_type": "application/pdf",
                "shared_with": 5,
                "created": "2026-02-15",
                "modified": "2026-03-04"
            },
            {
                "id": "doc-2",
                "name": "Budget Planning.xlsx",
                "owner": "Jane Smith",
                "file_size": 458932,
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "shared_with": 12,
                "created": "2026-01-20",
                "modified": "2026-03-02"
            },
            {
                "id": "doc-3",
                "name": "Presentation.pptx",
                "owner": "Bob Wilson",
                "file_size": 3928102,
                "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "shared_with": 3,
                "created": "2026-03-01",
                "modified": "2026-03-05"
            }
        ]
        
        log_access("list", "documents", "document")
        return api_response(data=documents)
    
    @app.route('/api/documents', methods=['POST'])
    def upload_document():
        """Upload a new document"""
        # In production, handle file upload here
        data = request.get_json() or {}
        doc_id = str(uuid.uuid4())
        
        new_doc = {
            "id": doc_id,
            "name": data.get('name', 'Untitled'),
            "owner": "current_user",
            "file_size": data.get('file_size', 0),
            "mime_type": data.get('mime_type', 'application/octet-stream'),
            "shared_with": 0,
            "created": datetime.utcnow().isoformat(),
            "modified": datetime.utcnow().isoformat()
        }
        
        documents_db[doc_id] = new_doc
        log_access("upload", doc_id, "document")
        
        return api_response(data=new_doc, status_code=201)
    
    @app.route('/api/documents/<doc_id>', methods=['GET'])
    def get_document(doc_id):
        """Get document details"""
        doc = documents_db.get(doc_id) or {
            "id": doc_id,
            "name": "Sample Document.pdf",
            "owner": "John Doe",
            "file_size": 2458624,
            "mime_type": "application/pdf"
        }
        
        log_access("view", doc_id, "document")
        return api_response(data=doc)
    
    @app.route('/api/documents/<doc_id>/share', methods=['POST'])
    def share_document(doc_id):
        """Share document with others"""
        data = request.get_json()
        recipients = data.get('recipients', [])
        permission = data.get('permission', 'view')  # view, comment, edit
        
        share_id = str(uuid.uuid4())
        share = {
            "id": share_id,
            "document_id": doc_id,
            "recipients": recipients,
            "permission": permission,
            "shared_at": datetime.utcnow().isoformat(),
            "expires_at": data.get('expires_at')
        }
        
        shares_db[share_id] = share
        log_access("share", doc_id, "document")
        
        return api_response(data=share, status_code=201)
    
    @app.route('/api/documents/<doc_id>/shares', methods=['GET'])
    def get_shares(doc_id):
        """Get sharing information for a document"""
        doc_shares = [s for s in shares_db.values() if s['document_id'] == doc_id]
        
        return api_response(data={
            "document_id": doc_id,
            "shares": doc_shares,
            "total_shared_with": len(doc_shares)
        })
    
    # =========== COMMENTS & DISCUSSIONS ===========
    @app.route('/api/documents/<doc_id>/comments', methods=['GET'])
    def get_comments(doc_id):
        """Get comments for a document"""
        comments = [
            {
                "id": "cmnt-1",
                "document_id": doc_id,
                "author": "John Doe",
                "content": "Great report! Need to review revenue projections.",
                "created": "2026-03-05 10:15:00",
                "replies": [
                    {
                        "id": "reply-1",
                        "author": "Jane Smith",
                        "content": "I'll check those numbers and get back to you.",
                        "created": "2026-03-05 10:45:00",
                        "reactions": {"likes": 1}
                    }
                ],
                "reactions": {"likes": 3, "loves": 1}
            },
            {
                "id": "cmnt-2",
                "document_id": doc_id,
                "author": "Bob Wilson",
                "content": "Can we update the charts before final review?",
                "created": "2026-03-04 14:30:00",
                "replies": [],
                "reactions": {"likes": 2}
            }
        ]
        
        log_access("view_comments", doc_id, "document")
        return api_response(data=comments)
    
    @app.route('/api/documents/<doc_id>/comments', methods=['POST'])
    def add_comment(doc_id):
        """Add a comment to a document"""
        data = request.get_json()
        comment_id = str(uuid.uuid4())
        
        comment = {
            "id": comment_id,
            "document_id": doc_id,
            "author": data.get('author', 'Anonymous'),
            "content": data.get('content', ''),
            "created": datetime.utcnow().isoformat(),
            "replies": [],
            "reactions": {"likes": 0, "loves": 0}
        }
        
        comments_db[comment_id] = comment
        log_access("add_comment", doc_id, "document")
        
        return api_response(data=comment, status_code=201)
    
    # =========== TEAMS & WORKSPACE ===========
    @app.route('/api/teams', methods=['GET'])
    def list_teams():
        """List all teams"""
        teams = [
            {
                "id": "team-1",
                "name": "Marketing Team",
                "description": "Marketing and content team",
                "members": 8,
                "created": "2026-01-15",
                "role": "member"
            },
            {
                "id": "team-2",
                "name": "Product Team",
                "description": "Product development and design",
                "members": 12,
                "created": "2026-02-01",
                "role": "admin"
            },
            {
                "id": "team-3",
                "name": "Finance Team",
                "description": "Financial planning and analysis",
                "members": 5,
                "created": "2026-02-20",
                "role": "member"
            }
        ]
        
        return api_response(data=teams)
    
    @app.route('/api/teams', methods=['POST'])
    def create_team():
        """Create a new team"""
        data = request.get_json()
        team_id = str(uuid.uuid4())
        
        new_team = {
            "id": team_id,
            "name": data.get('name', ''),
            "description": data.get('description', ''),
            "members": 1,
            "created": datetime.utcnow().isoformat(),
            "created_by": "current_user",
            "role": "admin"
        }
        
        teams_db[team_id] = new_team
        log_access("create", team_id, "team")
        
        return api_response(data=new_team, status_code=201)
    
    @app.route('/api/teams/<team_id>/members', methods=['GET'])
    def get_team_members(team_id):
        """Get team members"""
        members = [
            {
                "id": "user-1",
                "name": "John Doe",
                "email": "john@example.com",
                "role": "admin",
                "joined": "2026-01-15",
                "avatar": "https://api.example.com/avatar/user-1.jpg"
            },
            {
                "id": "user-2",
                "name": "Jane Smith",
                "email": "jane@example.com",
                "role": "member",
                "joined": "2026-01-20",
                "avatar": "https://api.example.com/avatar/user-2.jpg"
            },
            {
                "id": "user-3",
                "name": "Bob Wilson",
                "email": "bob@example.com",
                "role": "member",
                "joined": "2026-02-01",
                "avatar": "https://api.example.com/avatar/user-3.jpg"
            }
        ]
        
        return api_response(data=members)
    
    @app.route('/api/teams/<team_id>/projects', methods=['GET'])
    def get_team_projects(team_id):
        """Get projects in a team"""
        projects = [
            {
                "id": "proj-1",
                "name": "Website Redesign",
                "status": "in_progress",
                "progress": 65,
                "members": 4,
                "due_date": "2026-04-15"
            },
            {
                "id": "proj-2",
                "name": "Mobile App",
                "status": "planning",
                "progress": 20,
                "members": 6,
                "due_date": "2026-06-01"
            }
        ]
        
        return api_response(data=projects)
    
    # =========== ACCESS LOG & AUDIT ===========
    @app.route('/api/audit/logs', methods=['GET'])
    def get_audit_logs():
        """Get access audit logs"""
        action = request.args.get('action')
        user = request.args.get('user')
        
        # Filter logs
        logs = access_logs
        if action:
            logs = [l for l in logs if l['action'] == action]
        if user:
            logs = [l for l in logs if user in l.get('user_id', '')]
        
        return api_response(data={
            "total": len(logs),
            "logs": logs[-20:]  # Return last 20
        })
    
    # =========== NOTIFICATIONS ===========
    @app.route('/api/notifications', methods=['GET'])
    def get_notifications():
        """Get user notifications"""
        filter_type = request.args.get('filter')  # all, unread, shares, comments
        
        all_notifications = [
            {
                "id": "notf-1",
                "type": "document_shared",
                "title": "Document Shared",
                "message": "John Doe shared 'Q1 Report.pdf' with you",
                "read": False,
                "created": "2026-03-05 10:30:00",
                "link": "/documents/doc-1"
            },
            {
                "id": "notf-2",
                "type": "comment_added",
                "title": "New Comment",
                "message": "Jane Smith commented on 'Budget Planning.xlsx'",
                "read": True,
                "created": "2026-03-05 09:15:00",
                "link": "/documents/doc-2"
            },
            {
                "id": "notf-3",
                "type": "team_invitation",
                "title": "Team Invitation",
                "message": "You've been invited to join 'Finance Team'",
                "read": False,
                "created": "2026-03-04 16:45:00",
                "link": "/teams/team-3"
            }
        ]
        
        if filter_type == "unread":
            all_notifications = [n for n in all_notifications if not n['read']]
        elif filter_type == "shares":
            all_notifications = [n for n in all_notifications if n['type'] == 'document_shared']
        elif filter_type == "comments":
            all_notifications = [n for n in all_notifications if n['type'] == 'comment_added']
        
        return api_response(data={
            "total": len(all_notifications),
            "unread_count": len([n for n in all_notifications if not n['read']]),
            "notifications": all_notifications
        })
    
    @app.route('/api/notifications/<notf_id>', methods=['PUT'])
    def mark_notification_read(notf_id):
        """Mark notification as read"""
        # Would update in database
        return api_response(data={"id": notf_id, "read": True})
    
    @app.route('/api/notifications/preferences', methods=['GET'])
    def get_notification_preferences():
        """Get notification preferences"""
        preferences = {
            "email_notifications": True,
            "in_app_notifications": True,
            "document_shared": True,
            "comment_added": True,
            "team_invitation": True,
            "report_generated": True,
            "daily_digest": False,
            "unsubscribe_token": "secret-token-here"
        }
        
        return api_response(data=preferences)
    
    @app.route('/api/notifications/preferences', methods=['POST'])
    def update_notification_preferences():
        """Update notification preferences"""
        data = request.get_json()
        
        updated = {
            "email_notifications": data.get('email_notifications', True),
            "in_app_notifications": data.get('in_app_notifications', True),
            "document_shared": data.get('document_shared', True),
            "comment_added": data.get('comment_added', True),
            "team_invitation": data.get('team_invitation', True),
            "report_generated": data.get('report_generated', True),
            "daily_digest": data.get('daily_digest', False)
        }
        
        return api_response(data=updated)
    
    # =========== PERMISSIONS & ROLES ===========
    @app.route('/api/permissions/matrix', methods=['GET'])
    def get_permissions_matrix():
        """Get role × permission matrix"""
        matrix = {
            "roles": ["Viewer", "Editor", "Admin"],
            "permissions": [
                "View", "Download", "Comment", "Edit", 
                "Export", "Share", "Manage"
            ],
            "matrix": [
                [True, True, True, False, False, False, False],   # Viewer
                [True, True, True, True, True, True, False],      # Editor
                [True, True, True, True, True, True, True]        # Admin
            ]
        }
        
        return api_response(data=matrix)
    
    @app.route('/api/permissions/roles', methods=['GET'])
    def get_roles():
        """Get all roles"""
        roles = [
            {
                "id": "role-1",
                "name": "Viewer",
                "description": "Read-only access",
                "permissions": ["view", "download"]
            },
            {
                "id": "role-2",
                "name": "Editor",
                "description": "Can view and edit",
                "permissions": ["view", "download", "comment", "edit", "export", "share"]
            },
            {
                "id": "role-3",
                "name": "Admin",
                "description": "Full access",
                "permissions": ["view", "download", "comment", "edit", "export", "share", "manage"]
            }
        ]
        
        return api_response(data=roles)


# Export function for use in main server.py
def init_collaboration_api(app):
    """Initialize collaboration API endpoints"""
    register_collaboration_api(app)
