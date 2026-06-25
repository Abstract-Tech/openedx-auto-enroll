"""
Common Django settings for openedx_auto_enroll.
"""

SECRET_KEY = "secret-key"

INSTALLED_APPS = []

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_TZ = True


def plugin_settings(settings):
    """
    Set plugin defaults used by the Open edX platform.
    """
    settings.OPENEDX_AUTO_ENROLL_ENROLLMENT_MODE = "audit"
