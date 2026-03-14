"""OpenAPI and Swagger UI endpoints for the active Flask API surface."""

from __future__ import annotations

from copy import deepcopy
import inspect
import re

from flask import Blueprint, current_app, jsonify

bp = Blueprint('api_docs', __name__, url_prefix='/api')

_PARAM_PATTERN = re.compile(r'<(?:(?P<converter>[^:<>]+):)?(?P<name>[^<>]+)>')
_EXCLUDED_PREFIXES = ('/static/', '/swaggerui/')
_UNAUTHENTICATED_PATHS = {
    '/api/auth/login',
    '/api/auth/logout',
    '/api/auth/register',
    '/api/health',
    '/api/health/live',
    '/api/health/metrics',
    '/api/health/ready',
    '/api/health/status',
    '/api/openapi.json',
}
_UPLOAD_API_KEY_PATHS = {
    '/api/upload-chunk',
    '/api/upload-status',
    '/api/convert-uploaded',
    '/api/admin/purge-uploads',
}
_TAGS = {
    'account': 'Account and subscription management endpoints.',
    'admin': 'Administrative and operator-only APIs.',
    'analytics': 'Analytics, dashboards, and reporting endpoints.',
    'auth': 'Authentication and session management APIs.',
    'collaboration': 'Collaboration, documents, teams, and notification APIs.',
    'health': 'Health checks and runtime monitoring endpoints.',
    'notifications': 'Notification preference and delivery APIs.',
    'reports': 'Report lifecycle and export endpoints.',
    'upload': 'Chunked upload and conversion endpoints.',
}
_COMPONENT_SCHEMAS = {
    'ErrorResponse': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': False},
            'error': {'type': 'string', 'example': 'Invalid request'},
            'message': {'type': 'string', 'example': 'Unable to process request'},
        },
    },
    'HealthResponse': {
        'type': 'object',
        'properties': {
            'status': {'type': 'string', 'example': 'ok'},
        },
        'required': ['status'],
    },
    'AuthLoginRequest': {
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'example': 'jane'},
            'password': {'type': 'string', 'format': 'password'},
        },
        'required': ['username', 'password'],
    },
    'AuthRegisterRequest': {
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'example': 'jane'},
            'email': {'type': 'string', 'format': 'email', 'example': 'jane@example.com'},
            'password': {'type': 'string', 'format': 'password'},
        },
        'required': ['username', 'email', 'password'],
    },
    'UserSummary': {
        'type': 'object',
        'properties': {
            'id': {'type': 'integer', 'example': 42},
            'username': {'type': 'string', 'example': 'jane'},
            'email': {'type': 'string', 'format': 'email', 'example': 'jane@example.com'},
            'role': {'type': 'string', 'example': 'user'},
            'name': {'type': 'string', 'example': 'Jane'},
        },
    },
    'AuthSuccessResponse': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': True},
            'token': {'type': 'string', 'example': 'eyJhbGciOi...'},
            'user_id': {'type': 'integer', 'example': 42},
            'api_key': {'type': 'string', 'example': 'docpro_live_key'},
            'message': {'type': 'string', 'example': 'Login successful'},
            'user': {'$ref': '#/components/schemas/UserSummary'},
        },
    },
    'GenericSuccessEnvelope': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': True},
            'data': {'type': 'object'},
            'message': {'type': 'string'},
        },
    },
    'AnalyticsDashboardResponse': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': True},
            'data': {
                'type': 'object',
                'properties': {
                    'kpis': {'type': 'array', 'items': {'type': 'object'}},
                    'charts': {'type': 'array', 'items': {'type': 'object'}},
                },
            },
        },
    },
    'UploadChunkResponse': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': True},
            'upload_id': {'type': 'string', 'example': 'upload-1'},
            'filename': {'type': 'string', 'example': 'sample.png'},
            'assembled': {'type': 'boolean', 'example': False},
            'assembled_path': {'type': 'string', 'nullable': True},
        },
    },
    'UploadStatusResponse': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': True},
            'chunks': {'type': 'array', 'items': {'type': 'integer'}},
            'total': {'type': 'integer', 'nullable': True},
        },
    },
    'ConvertUploadedRequest': {
        'type': 'object',
        'properties': {
            'uploads': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'upload_id': {'type': 'string'},
                        'filename': {'type': 'string'},
                    },
                    'required': ['upload_id', 'filename'],
                },
            },
            'target_format': {'type': 'string', 'example': 'jpg'},
            'preset': {'type': 'string', 'nullable': True},
            'quality': {'type': 'integer', 'example': 80},
            'lossless': {'type': 'boolean', 'example': False},
        },
        'required': ['uploads', 'target_format'],
    },
    'ReportsListResponse': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': True},
            'data': {'type': 'array', 'items': {'type': 'object'}},
        },
    },
    'ReportCreateRequest': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'example': 'Monthly usage'},
            'description': {'type': 'string'},
            'report_type': {'type': 'string', 'example': 'usage'},
            'export_format': {'type': 'string', 'example': 'pdf'},
            'config': {'type': 'object'},
        },
        'required': ['name'],
    },
    'ReportResponse': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': True},
            'data': {'type': 'object'},
        },
    },
    'AdminUsersResponse': {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean', 'example': True},
            'users': {'type': 'array', 'items': {'$ref': '#/components/schemas/UserSummary'}},
            'pagination': {
                'type': 'object',
                'properties': {
                    'page': {'type': 'integer', 'example': 1},
                    'per_page': {'type': 'integer', 'example': 25},
                },
            },
        },
    },
}
_COMMON_QUERY_PARAMETERS = {
    'page': {
        'name': 'page',
        'in': 'query',
        'required': False,
        'schema': {'type': 'integer', 'default': 1, 'minimum': 1},
        'description': 'Page number for paginated responses.',
    },
    'per_page': {
        'name': 'per_page',
        'in': 'query',
        'required': False,
        'schema': {'type': 'integer', 'default': 25, 'minimum': 1},
        'description': 'Number of records to return per page.',
    },
}
_ROUTE_OVERRIDES = {
    '/api/health': {
        'get': {
            'tags': ['health'],
            'responses': {
                '200': {
                    'description': 'Basic health response.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/HealthResponse'}}},
                }
            },
            'security': [],
        }
    },
    '/api/auth/login': {
        'post': {
            'tags': ['auth'],
            'requestBody': {
                'required': True,
                'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AuthLoginRequest'}}},
            },
            'responses': {
                '200': {
                    'description': 'User authenticated.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AuthSuccessResponse'}}},
                },
                '401': {
                    'description': 'Invalid credentials.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ErrorResponse'}}},
                },
            },
            'security': [],
        }
    },
    '/api/auth/register': {
        'post': {
            'tags': ['auth'],
            'requestBody': {
                'required': True,
                'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AuthRegisterRequest'}}},
            },
            'responses': {
                '201': {
                    'description': 'User registered.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AuthSuccessResponse'}}},
                },
                '400': {
                    'description': 'Invalid registration payload.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ErrorResponse'}}},
                },
            },
            'security': [],
        }
    },
    '/api/auth/logout': {
        'post': {
            'tags': ['auth'],
            'responses': {
                '200': {
                    'description': 'Session cleared.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/GenericSuccessEnvelope'}}},
                }
            },
            'security': [],
        }
    },
    '/api/analytics/dashboard': {
        'get': {
            'tags': ['analytics'],
            'responses': {
                '200': {
                    'description': 'Analytics dashboard payload.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AnalyticsDashboardResponse'}}},
                }
            },
        }
    },
    '/api/reports': {
        'get': {
            'tags': ['reports'],
            'responses': {
                '200': {
                    'description': 'List reports for the current user.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ReportsListResponse'}}},
                }
            },
        },
        'post': {
            'tags': ['reports'],
            'requestBody': {
                'required': True,
                'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ReportCreateRequest'}}},
            },
            'responses': {
                '201': {
                    'description': 'Report created.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ReportResponse'}}},
                }
            },
        },
    },
    '/api/upload-chunk': {
        'post': {
            'tags': ['upload'],
            'responses': {
                '200': {
                    'description': 'Chunk accepted and upload state updated.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/UploadChunkResponse'}}},
                }
            },
        }
    },
    '/api/upload-status': {
        'get': {
            'tags': ['upload'],
            'parameters': [{
                'name': 'upload_id',
                'in': 'query',
                'required': True,
                'schema': {'type': 'string'},
                'description': 'Upload identifier returned by the chunk upload endpoint.',
            }],
            'responses': {
                '200': {
                    'description': 'Current chunk upload state.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/UploadStatusResponse'}}},
                }
            },
        }
    },
    '/api/convert-uploaded': {
        'post': {
            'tags': ['upload'],
            'requestBody': {
                'required': True,
                'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ConvertUploadedRequest'}}},
            },
            'responses': {
                '200': {
                    'description': 'Converted file download or zip archive.',
                    'content': {
                        'application/octet-stream': {'schema': {'type': 'string', 'format': 'binary'}},
                        'application/zip': {'schema': {'type': 'string', 'format': 'binary'}},
                    },
                }
            },
        }
    },
    '/api/admin/users': {
        'get': {
            'tags': ['admin'],
            'parameters': [_COMMON_QUERY_PARAMETERS['page'], _COMMON_QUERY_PARAMETERS['per_page']],
            'responses': {
                '200': {
                    'description': 'Paginated list of users.',
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/AdminUsersResponse'}}},
                }
            },
        }
    },
}


def _normalize_rule(rule_string: str) -> str:
    def replacer(match):
        return '{' + match.group('name') + '}'

    return _PARAM_PATTERN.sub(replacer, rule_string)


def _extract_path_parameters(rule_string: str):
    parameters = []
    for match in _PARAM_PATTERN.finditer(rule_string):
        converter = match.group('converter') or 'string'
        schema_type = 'integer' if converter == 'int' else 'string'
        parameters.append({
            'name': match.group('name'),
            'in': 'path',
            'required': True,
            'schema': {'type': schema_type},
        })
    return parameters


def _tag_for_rule(path: str, endpoint: str) -> str:
    parts = [segment for segment in path.split('/') if segment]
    if not parts:
        return endpoint.split('.', 1)[0]

    if parts[0] == 'api' and len(parts) > 1:
        return parts[1]

    return parts[0]


def _security_for_path(path: str):
    if path in _UNAUTHENTICATED_PATHS:
        return []
    if path in _UPLOAD_API_KEY_PATHS:
        return [{'ApiKeyAuth': []}]
    if path.startswith('/api/'):
        return [{'BearerAuth': []}]
    return []


def _request_body_for_operation(path: str, method: str):
    if method not in {'post', 'put', 'patch'}:
        return None

    if path == '/api/upload-chunk':
        return {
            'required': True,
            'content': {
                'multipart/form-data': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'chunk': {'type': 'string', 'format': 'binary'},
                            'upload_id': {'type': 'string'},
                            'filename': {'type': 'string'},
                            'index': {'type': 'integer'},
                            'total': {'type': 'integer'},
                        },
                        'required': ['chunk'],
                    }
                }
            },
        }

    return {
        'required': False,
        'content': {
            'application/json': {
                'schema': {'type': 'object'}
            }
        },
    }


def _default_responses(path: str, method: str):
    if path == '/api/convert-uploaded' and method == 'post':
        return {
            '200': {
                'description': 'Converted file download.',
                'content': {'application/octet-stream': {'schema': {'type': 'string', 'format': 'binary'}}},
            },
            '400': {'description': 'Bad request'},
            '401': {'description': 'Unauthorized'},
            '500': {'description': 'Internal server error'},
        }

    return {
        '200': {
            'description': 'Successful response',
            'content': {'application/json': {'schema': {'$ref': '#/components/schemas/GenericSuccessEnvelope'}}},
        },
        '400': {
            'description': 'Bad request',
            'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ErrorResponse'}}},
        },
        '401': {
            'description': 'Unauthorized',
            'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ErrorResponse'}}},
        },
        '500': {
            'description': 'Internal server error',
            'content': {'application/json': {'schema': {'$ref': '#/components/schemas/ErrorResponse'}}},
        },
    }


def _merge_operation(operation, override):
    merged = deepcopy(operation)
    for key, value in override.items():
        if key in {'responses', 'content'} and isinstance(value, dict):
            merged.setdefault(key, {})
            merged[key].update(deepcopy(value))
            continue
        if key == 'parameters' and value is not None:
            merged[key] = deepcopy(value)
            continue
        merged[key] = deepcopy(value)
    return merged


def build_openapi_spec(app):
    paths = {}

    for rule in sorted(app.url_map.iter_rules(), key=lambda item: item.rule):
        if any(rule.rule.startswith(prefix) for prefix in _EXCLUDED_PREFIXES):
            continue
        if rule.endpoint == 'static':
            continue

        normalized_path = _normalize_rule(rule.rule)
        if not (normalized_path.startswith('/api/') or normalized_path.startswith('/health')):
            continue

        view = app.view_functions.get(rule.endpoint)
        if view is None:
            continue

        unwrapped_view = inspect.unwrap(view)
        docstring = inspect.getdoc(unwrapped_view) or 'No description available.'
        summary = docstring.splitlines()[0].strip()
        parameters = _extract_path_parameters(rule.rule)
        security = _security_for_path(normalized_path)
        tag = _tag_for_rule(normalized_path, rule.endpoint)

        path_item = paths.setdefault(normalized_path, {})
        for method in sorted(rule.methods - {'HEAD', 'OPTIONS'}):
            lower_method = method.lower()
            operation = {
                'tags': [tag],
                'summary': summary,
                'description': docstring,
                'operationId': f"{rule.endpoint.replace('.', '_')}_{lower_method}",
                'security': security,
                'responses': _default_responses(normalized_path, lower_method),
            }
            if parameters:
                operation['parameters'] = parameters

            request_body = _request_body_for_operation(normalized_path, lower_method)
            if request_body is not None:
                operation['requestBody'] = request_body

            if lower_method == 'post' and normalized_path.endswith('/register'):
                operation['responses']['201'] = {'description': 'Resource created'}

            override = _ROUTE_OVERRIDES.get(normalized_path, {}).get(lower_method)
            if override:
                operation = _merge_operation(operation, override)

            path_item[lower_method] = operation

    seen_tags = sorted({tag for path_item in paths.values() for operation in path_item.values() for tag in operation.get('tags', [])})

    return {
        'openapi': '3.0.3',
        'info': {
            'title': 'DocPro API',
            'version': '1.0.0',
            'description': 'Live OpenAPI document generated from the active Flask app route map.',
        },
        'servers': [{'url': '/'}],
        'components': {
            'securitySchemes': {
                'BearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT',
                },
                'ApiKeyAuth': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'X-API-Key',
                },
            },
            'schemas': deepcopy(_COMPONENT_SCHEMAS),
        },
        'tags': [{'name': tag, 'description': _TAGS.get(tag, f'{tag.title()} endpoints.')} for tag in seen_tags],
        'paths': paths,
    }


@bp.route('/openapi.json', methods=['GET'])
def openapi_spec():
    """Return the live OpenAPI specification for the active API routes."""
    return jsonify(build_openapi_spec(current_app._get_current_object()))


def register_swagger_ui(app):
    """Register Swagger UI if the optional dependency is available."""
    try:
        from flask_swagger_ui import get_swaggerui_blueprint
    except ImportError:
        app.logger.warning('flask_swagger_ui not installed - Swagger UI disabled')
        return False

    swaggerui_blueprint = get_swaggerui_blueprint(
        '/api/docs',
        '/api/openapi.json',
        config={
            'app_name': 'DocPro API',
            'deepLinking': True,
            'displayOperationId': True,
        },
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix='/api/docs')
    return True