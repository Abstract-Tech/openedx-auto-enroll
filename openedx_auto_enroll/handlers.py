"""
Open edX event handlers for automatic course enrollment.
"""

import logging

from django.contrib.auth import get_user_model
from django.dispatch import receiver
from openedx_events.learning.signals import STUDENT_REGISTRATION_COMPLETED

from openedx_auto_enroll.models import AutoEnrollConfiguration, AutoEnrollCourse

log = logging.getLogger(__name__)


@receiver(STUDENT_REGISTRATION_COMPLETED)
def auto_enroll_new_user(signal, sender, user, metadata, **kwargs):  # pylint: disable=unused-argument
    """
    Enroll a newly registered user in all enabled auto-enroll courses.
    """
    if not AutoEnrollConfiguration.is_enabled():
        log.debug("Open edX Auto Enroll is disabled; skipping user_id=%s.", user.id)
        return

    courses = list(AutoEnrollCourse.enabled_courses())
    if not courses:
        log.debug("No auto-enroll courses configured; skipping user_id=%s.", user.id)
        return

    User = get_user_model()  # pylint: disable=invalid-name
    try:
        django_user = User.objects.get(id=user.id)
    except User.DoesNotExist:
        log.warning("Could not auto-enroll missing user_id=%s.", user.id)
        return

    for course in courses:
        enroll_user_in_course(django_user, course)


def enroll_user_in_course(user, auto_enroll_course):
    """
    Enroll a Django user in a configured course.
    """
    try:
        from common.djangoapps.student.models import CourseEnrollment  # pylint: disable=import-outside-toplevel
        from opaque_keys.edx.keys import CourseKey  # pylint: disable=import-outside-toplevel

        course_key = CourseKey.from_string(auto_enroll_course.course_id)
        CourseEnrollment.enroll(
            user,
            course_key,
            mode=auto_enroll_course.enrollment_mode,
        )
    except Exception:  # pylint: disable=broad-exception-caught
        log.exception(
            "Failed to auto-enroll user_id=%s in course_id=%s.",
            user.id,
            auto_enroll_course.course_id,
        )
