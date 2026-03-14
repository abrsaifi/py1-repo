"""Compatibility tests for legacy Phase 15 registration shims."""
from flask import Flask

from analytics_api import init_analytics_api
from collaboration_api import init_collaboration_api


def test_legacy_phase15_analytics_wrapper_registers_blueprint():
    app = Flask(__name__)

    init_analytics_api(app)

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert '/api/analytics/dashboard' in rules
    assert '/api/reports' in rules


def test_legacy_phase15_collaboration_wrapper_registers_blueprint():
    app = Flask(__name__)

    init_collaboration_api(app)

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert '/api/collaboration/dashboard' in rules
    assert '/api/notifications' in rules