import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEPLOYMENT_ENVIRONMENT_VARIABLES = (
    "DJANGO_SECRET_KEY",
    "DJANGO_DEBUG",
    "DJANGO_ALLOWED_HOSTS",
    "DJANGO_SERVE_MEDIA",
    "DJANGO_SECURE_SSL_REDIRECT",
    "DJANGO_SESSION_COOKIE_SECURE",
    "DJANGO_CSRF_COOKIE_SECURE",
    "DJANGO_SECURE_HSTS_SECONDS",
)


def _settings_process(environment_updates, script):
    environment = os.environ.copy()
    for variable_name in DEPLOYMENT_ENVIRONMENT_VARIABLES:
        environment.pop(variable_name, None)
    environment.update(environment_updates)
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_production_environment_configures_hosts_static_and_security():
    result = _settings_process(
        {
            "DJANGO_SECRET_KEY": "production-test-secret-" + ("x" * 40),
            "DJANGO_DEBUG": "false",
            "DJANGO_ALLOWED_HOSTS": "127.0.0.1, localhost",
            "DJANGO_SERVE_MEDIA": "true",
            "DJANGO_SECURE_SSL_REDIRECT": "true",
            "DJANGO_SESSION_COOKIE_SECURE": "true",
            "DJANGO_CSRF_COOKIE_SECURE": "true",
            "DJANGO_SECURE_HSTS_SECONDS": "31536000",
        },
        (
            "import json; from config import settings; "
            "print(json.dumps({"
            "'debug': settings.DEBUG, "
            "'allowed_hosts': settings.ALLOWED_HOSTS, "
            "'serve_media': settings.SERVE_MEDIA, "
            "'static_root': settings.STATIC_ROOT.name, "
            "'media_root': settings.MEDIA_ROOT.name, "
            "'middleware': settings.MIDDLEWARE[:2], "
            "'static_backend': settings.STORAGES['staticfiles']['BACKEND'], "
            "'ssl_redirect': settings.SECURE_SSL_REDIRECT, "
            "'secure_session': settings.SESSION_COOKIE_SECURE, "
            "'secure_csrf': settings.CSRF_COOKIE_SECURE, "
            "'hsts': settings.SECURE_HSTS_SECONDS"
            "}))"
        ),
    )

    assert result.returncode == 0, result.stderr
    settings_data = json.loads(result.stdout)
    assert settings_data == {
        "debug": False,
        "allowed_hosts": ["127.0.0.1", "localhost"],
        "serve_media": True,
        "static_root": "staticfiles",
        "media_root": "media",
        "middleware": [
            "django.middleware.security.SecurityMiddleware",
            "whitenoise.middleware.WhiteNoiseMiddleware",
        ],
        "static_backend": ("whitenoise.storage.CompressedManifestStaticFilesStorage"),
        "ssl_redirect": True,
        "secure_session": True,
        "secure_csrf": True,
        "hsts": 31536000,
    }


@pytest.mark.parametrize(
    ("environment_updates", "expected_error"),
    [
        (
            {
                "DJANGO_DEBUG": "false",
                "DJANGO_ALLOWED_HOSTS": "localhost",
            },
            "DJANGO_SECRET_KEY is required",
        ),
        (
            {
                "DJANGO_DEBUG": "false",
                "DJANGO_SECRET_KEY": "production-test-secret",
            },
            "DJANGO_ALLOWED_HOSTS is required",
        ),
        (
            {"DJANGO_DEBUG": "sometimes"},
            "DJANGO_DEBUG must be one of",
        ),
        (
            {"DJANGO_SECURE_HSTS_SECONDS": "-1"},
            "DJANGO_SECURE_HSTS_SECONDS must be a non-negative integer",
        ),
    ],
)
def test_invalid_production_environment_fails_closed(
    environment_updates,
    expected_error,
):
    result = _settings_process(
        environment_updates,
        "from config import settings",
    )

    assert result.returncode != 0
    assert expected_error in result.stderr
