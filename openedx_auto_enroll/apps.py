"""
openedx_auto_enroll Django application initialization.
"""

from django.apps import AppConfig


class OpenedxAutoEnrollConfig(AppConfig):
    """
    Configuration for the openedx_auto_enroll Django application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "openedx_auto_enroll"
    verbose_name = "Open edX Auto Enroll"

    plugin_app = {
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
        },
    }

    def ready(self):
        """Import signal handlers when Django starts."""
        from openedx_auto_enroll import handlers  # pylint: disable=unused-import, import-outside-toplevel
