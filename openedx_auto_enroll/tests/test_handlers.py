"""
Tests for Open edX Auto Enroll event handlers.
"""

from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from openedx_auto_enroll.handlers import auto_enroll_new_user
from openedx_auto_enroll.models import AutoEnrollConfiguration, AutoEnrollCourse


class AutoEnrollNewUserTest(TestCase):
    """
    Tests for enrolling new users in configured courses.
    """

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username="new-user",
            email="new-user@example.com",
            password="password",
        )
        self.event_user = SimpleNamespace(id=self.user.id)

    @patch("openedx_auto_enroll.handlers.enroll_user_in_course")
    def test_auto_enrolls_new_user_in_enabled_courses(self, enroll_mock):
        """
        New users are enrolled in enabled courses when the plugin is enabled.
        """
        enabled_course = AutoEnrollCourse.objects.create(course_id="course-v1:edX+DemoX+Demo_Course")
        AutoEnrollCourse.objects.create(
            course_id="course-v1:edX+Disabled+Demo_Course",
            enabled=False,
        )

        auto_enroll_new_user(None, None, self.event_user, None)

        enroll_mock.assert_called_once_with(self.user, enabled_course)

    @patch("openedx_auto_enroll.handlers.enroll_user_in_course")
    def test_skips_when_globally_disabled(self, enroll_mock):
        """
        No enrollments happen when the global switch is disabled.
        """
        AutoEnrollConfiguration.objects.create(enabled=False)
        AutoEnrollCourse.objects.create(course_id="course-v1:edX+DemoX+Demo_Course")

        auto_enroll_new_user(None, None, self.event_user, None)

        enroll_mock.assert_not_called()

    @patch("openedx_auto_enroll.handlers.enroll_user_in_course")
    def test_skips_missing_user(self, enroll_mock):
        """
        Missing Django users are ignored.
        """
        AutoEnrollCourse.objects.create(course_id="course-v1:edX+DemoX+Demo_Course")

        auto_enroll_new_user(None, None, SimpleNamespace(id=self.user.id + 1), None)

        enroll_mock.assert_not_called()
