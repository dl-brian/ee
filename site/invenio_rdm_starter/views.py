"""Additional views."""

from functools import wraps

from flask import Blueprint, abort, request
from invenio_administration.permissions import administration_permission
from prometheus_flask_exporter import PrometheusMetrics


def _metrics_access(f):
    """Allow direct internal requests; require admin permission via proxy."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get("X-Forwarded-For"):
            # Request came through the upstream proxy — enforce auth
            if not administration_permission.can():
                abort(403)
        return f(*args, **kwargs)

    return decorated


def create_api_blueprint(app):
    """Register Prometheus metrics on the API Flask app."""
    metrics = PrometheusMetrics(
        app,
        path="/api/metrics",
        group_by="endpoint",
        metrics_decorator=_metrics_access,
    )
    # Disable HTTPS redirect for /api/metrics so internal Prometheus scrapers
    # can reach it without TLS (same pattern as /ping).
    metrics_view = app.view_functions.get("prometheus_metrics")
    if metrics_view is not None:
        metrics_view.talisman_view_options = {"force_https": False}
    return Blueprint("rogue_scholar_api", __name__)


#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app."""
    # Track UI app requests in the shared multiprocess registry.
    # metrics_endpoint=False avoids registering a duplicate metrics route
    # (that lives on the API app via create_api_blueprint).
    PrometheusMetrics(
        app, group_by="endpoint", export_defaults=True, metrics_endpoint=False
    )

    blueprint = Blueprint(
        "invenio_rdm_starter",
        __name__,
        template_folder="./templates",
    )

    # Add URL rules
    return blueprint
