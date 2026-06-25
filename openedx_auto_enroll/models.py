"""
Database models for Open edX Auto Enroll.
"""

from django.db import models


class AutoEnrollConfiguration(models.Model):
    """
    Global configuration for automatic enrollment.
    """

    singleton_id = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)
    enabled = models.BooleanField(
        default=True,
        help_text="Enroll newly registered users in the enabled courses below.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Auto enroll configuration"
        verbose_name_plural = "Auto enroll configuration"

    def __str__(self):
        status = "enabled" if self.enabled else "disabled"
        return f"Auto enroll is {status}"

    @classmethod
    def is_enabled(cls):
        """
        Return whether auto-enrollment is globally enabled.
        """
        config = cls.objects.order_by("id").first()
        return True if config is None else config.enabled


class AutoEnrollCourse(models.Model):
    """
    A course that newly registered users should be enrolled in.
    """

    AUDIT = "audit"
    HONOR = "honor"
    VERIFIED = "verified"

    ENROLLMENT_MODE_CHOICES = (
        (AUDIT, "Audit"),
        (HONOR, "Honor"),
        (VERIFIED, "Verified"),
    )

    course_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Open edX course key, for example course-v1:edX+DemoX+Demo_Course.",
    )
    enrollment_mode = models.CharField(
        max_length=32,
        choices=ENROLLMENT_MODE_CHOICES,
        default=AUDIT,
    )
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("course_id",)
        verbose_name = "Auto enroll course"
        verbose_name_plural = "Auto enroll courses"

    def __str__(self):
        status = "enabled" if self.enabled else "disabled"
        return f"{self.course_id} ({self.enrollment_mode}, {status})"

    @classmethod
    def enabled_courses(cls):
        """
        Return enabled course rows for automatic enrollment.
        """
        return cls.objects.filter(enabled=True).order_by("course_id")
