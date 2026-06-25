# Generated for openedx_auto_enroll.

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Initial Open edX Auto Enroll models.
    """

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AutoEnrollConfiguration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("singleton_id", models.PositiveSmallIntegerField(default=1, editable=False, unique=True)),
                (
                    "enabled",
                    models.BooleanField(
                        default=True,
                        help_text="Enroll newly registered users in the enabled courses below.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Auto enroll configuration",
                "verbose_name_plural": "Auto enroll configuration",
            },
        ),
        migrations.CreateModel(
            name="AutoEnrollCourse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "course_id",
                    models.CharField(
                        help_text="Open edX course key, for example course-v1:edX+DemoX+Demo_Course.",
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    "enrollment_mode",
                    models.CharField(
                        choices=[("audit", "Audit"), ("honor", "Honor"), ("verified", "Verified")],
                        default="audit",
                        max_length=32,
                    ),
                ),
                ("enabled", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Auto enroll course",
                "verbose_name_plural": "Auto enroll courses",
                "ordering": ("course_id",),
            },
        ),
    ]
