"""Tests for Prometheus metrics endpoint wiring."""

import tempfile
import unittest
from unittest.mock import patch

from flask import Flask

from invenio_rdm_starter.views import create_api_blueprint, create_blueprint


class MetricsEndpointTestCase(unittest.TestCase):
    """Ensure metrics endpoint wiring and access rules are correct."""

    def _create_app_with_metrics(self):
        app = Flask(__name__)
        create_api_blueprint(app)
        return app

    def _create_ui_app_with_metrics(self):
        app = Flask(__name__)
        create_blueprint(app)
        return app

    def test_api_metrics_endpoint_exists(self):
        with tempfile.TemporaryDirectory() as multiproc_dir:
            with patch.dict(
                "os.environ",
                {"PROMETHEUS_MULTIPROC_DIR": multiproc_dir},
                clear=False,
            ):
                app = self._create_app_with_metrics()
                client = app.test_client()
                response = client.get("/metrics")

                self.assertEqual(response.status_code, 200)
                self.assertIn("text/plain", response.content_type)

    def test_api_metrics_requires_admin_when_forwarded(self):
        with tempfile.TemporaryDirectory() as multiproc_dir:
            with patch.dict(
                "os.environ",
                {"PROMETHEUS_MULTIPROC_DIR": multiproc_dir},
                clear=False,
            ):
                app = self._create_app_with_metrics()
                client = app.test_client()

                with patch(
                    "invenio_rdm_starter.views.administration_permission.can",
                    return_value=False,
                ):
                    response = client.get(
                        "/metrics",
                        headers={"X-Forwarded-For": "10.0.0.1"},
                    )

                self.assertEqual(response.status_code, 403)

    def test_api_metrics_allows_admin_when_forwarded(self):
        with tempfile.TemporaryDirectory() as multiproc_dir:
            with patch.dict(
                "os.environ",
                {"PROMETHEUS_MULTIPROC_DIR": multiproc_dir},
                clear=False,
            ):
                app = self._create_app_with_metrics()
                client = app.test_client()

                with patch(
                    "invenio_rdm_starter.views.administration_permission.can",
                    return_value=True,
                ):
                    response = client.get(
                        "/metrics",
                        headers={"X-Forwarded-For": "10.0.0.1"},
                    )

                self.assertEqual(response.status_code, 200)

    def test_ui_app_does_not_expose_metrics_endpoint(self):
        with tempfile.TemporaryDirectory() as multiproc_dir:
            with patch.dict(
                "os.environ",
                {"PROMETHEUS_MULTIPROC_DIR": multiproc_dir},
                clear=False,
            ):
                app = self._create_ui_app_with_metrics()
                client = app.test_client()
                response = client.get("/metrics")

                self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
