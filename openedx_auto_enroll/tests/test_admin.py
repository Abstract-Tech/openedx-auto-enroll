"""
Tests for Open edX Auto Enroll admin behavior.
"""

import json
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from django.contrib import admin
from django.test import RequestFactory, SimpleTestCase

from openedx_auto_enroll.admin import AutoEnrollCourseAdmin, CourseOverviewAutocompleteWidget
from openedx_auto_enroll.models import AutoEnrollCourse


class StaffUser:
    """
    Minimal staff user for ModelAdmin permission checks.
    """

    is_active = True
    is_staff = True

    def has_perm(self, permission):  # pylint: disable=unused-argument
        return True


class CourseOverviewQuerySet(list):
    """
    Minimal queryset-like list for CourseOverview autocomplete tests.
    """

    def order_by(self, field_name):  # pylint: disable=unused-argument
        return self

    def filter(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self


class CourseOverviewManager:
    """
    Minimal CourseOverview manager for autocomplete tests.
    """

    def __init__(self, courses):
        self.courses = CourseOverviewQuerySet(courses)

    def all(self):
        return self.courses


def course_overview_modules(courses):
    """
    Return mocked Open edX CourseOverview import modules.
    """
    modules = {
        "openedx": ModuleType("openedx"),
        "openedx.core": ModuleType("openedx.core"),
        "openedx.core.djangoapps": ModuleType("openedx.core.djangoapps"),
        "openedx.core.djangoapps.content": ModuleType("openedx.core.djangoapps.content"),
        "openedx.core.djangoapps.content.course_overviews": ModuleType(
            "openedx.core.djangoapps.content.course_overviews"
        ),
        "openedx.core.djangoapps.content.course_overviews.models": ModuleType(
            "openedx.core.djangoapps.content.course_overviews.models"
        ),
    }

    class CourseOverview:
        objects = CourseOverviewManager(courses)

    modules["openedx.core.djangoapps.content.course_overviews.models"].CourseOverview = CourseOverview
    return modules


class AutoEnrollCourseAdminTest(SimpleTestCase):
    """
    Tests for the AutoEnrollCourse admin.
    """

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.model_admin = AutoEnrollCourseAdmin(AutoEnrollCourse, admin.site)

    def test_course_id_uses_course_overview_autocomplete_widget(self):
        """
        The course_id CharField renders with the CourseOverview autocomplete widget.
        """
        request = self.factory.get("/")
        request.user = StaffUser()
        field = AutoEnrollCourse._meta.get_field("course_id")

        form_field = self.model_admin.formfield_for_dbfield(field, request)

        self.assertIsInstance(form_field.widget, CourseOverviewAutocompleteWidget)

    def test_course_overview_autocomplete_returns_select2_results(self):
        """
        The custom admin endpoint returns CourseOverview rows in Select2 format.
        """
        courses = [
            SimpleNamespace(id="course-v1:edX+DemoX+Demo_Course", display_name="Demonstration Course"),
        ]
        request = self.factory.get("/?term=Demo")
        request.user = StaffUser()

        with patch.dict(sys.modules, course_overview_modules(courses)):
            response = self.model_admin.course_overview_autocomplete(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(
            data,
            {
                "results": [
                    {
                        "id": "course-v1:edX+DemoX+Demo_Course",
                        "text": "course-v1:edX+DemoX+Demo_Course - Demonstration Course",
                    }
                ],
                "pagination": {"more": False},
            },
        )

