"""
Django settings module.

This module determines which settings to use based on the DJANGO_SETTINGS_MODULE
environment variable. Default is development settings.
"""

import os

environment = os.environ.get("DJANGO_ENV", "development")

if environment == "production":
    from .production import *  # noqa: F401, F403
elif environment == "testing":
    from .testing import *  # noqa: F401, F403
else:
    from .development import *  # noqa: F401, F403
