"""
Django admin configuration for Open edX Auto Enroll.
"""

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.widgets import get_select2_language
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.urls import path, reverse

from openedx_auto_enroll.models import AutoEnrollConfiguration, AutoEnrollCourse


def get_course_overview_model():  # pylint: disable=import-outside-toplevel
    """
    Import CourseOverview lazily so this module can load outside Open edX.
    """
    from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

    return CourseOverview


class CourseOverviewAutocompleteWidget(forms.Select):
    """
    Select2-backed widget that stores the selected CourseOverview id as text.
    """

    def __init__(self, admin_site, attrs=None, choices=()):
        self.admin_site = admin_site
        self.i18n_name = get_select2_language()
        super().__init__(attrs=attrs, choices=choices)

    def get_url(self):
        """
        Return the auto-enroll admin URL that searches CourseOverview rows.
        """
        return reverse(
            "%s:openedx_auto_enroll_autoenrollcourse_course_overview_autocomplete"
            % self.admin_site.name
        )

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Add the data attributes expected by django.contrib.admin's Select2 init.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault("class", "")
        attrs.update(
            {
                "data-ajax--cache": "true",
                "data-ajax--delay": 250,
                "data-ajax--type": "GET",
                "data-ajax--url": self.get_url(),
                "data-theme": "admin-autocomplete",
                "data-allow-clear": "false",
                "data-placeholder": "Search for a course",
                "lang": self.i18n_name,
                "class": attrs["class"] + (" " if attrs["class"] else "") + "admin-autocomplete",
            }
        )
        return attrs

    def optgroups(self, name, value, attrs=None):
        """
        Preserve the current saved course key as the selected Select2 option.
        """
        selected_choices = {str(item) for item in value if item}
        groups = [(None, [], 0)]

        for index, option_value in enumerate(selected_choices):
            groups[0][1].append(
                self.create_option(
                    name,
                    option_value,
                    self.label_for_value(option_value),
                    True,
                    index,
                    attrs=attrs,
                )
            )

        return groups

    def label_for_value(self, value):
        """
        Return a readable label for a course key when CourseOverview is available.
        """
        try:
            course = get_course_overview_model().objects.get(id=value)
        except Exception:  # pylint: disable=broad-exception-caught
            return value

        if course.display_name:
            return f"{course.id} - {course.display_name}"
        return str(course.id)

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        i18n_file = (
            ("admin/js/vendor/select2/i18n/%s.js" % self.i18n_name,)
            if self.i18n_name
            else ()
        )
        return forms.Media(
            js=(
                "admin/js/vendor/jquery/jquery%s.js" % extra,
                "admin/js/vendor/select2/select2.full%s.js" % extra,
            )
            + i18n_file
            + (
                "admin/js/jquery.init.js",
                "admin/js/autocomplete.js",
            ),
            css={
                "screen": (
                    "admin/css/vendor/select2/select2%s.css" % extra,
                    "admin/css/autocomplete.css",
                ),
            },
        )


class AutoEnrollConfigurationAdmin(admin.ModelAdmin):
    """
    Admin controls for the global auto-enroll switch.
    """

    list_display = ("enabled", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        """
        Allow only one configuration row.
        """
        if AutoEnrollConfiguration.objects.exists():
            return False
        return super().has_add_permission(request)


class AutoEnrollCourseForm(forms.ModelForm):
    """
    Validate course keys before saving auto-enroll course rows.
    """

    class Meta:
        model = AutoEnrollCourse
        fields = "__all__"

    def clean_course_id(self):
        """
        Validate that course_id is a parseable Open edX course key.
        """
        course_id = self.cleaned_data["course_id"].strip()

        try:
            from opaque_keys.edx.keys import CourseKey  # pylint: disable=import-outside-toplevel

            CourseKey.from_string(course_id)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            raise forms.ValidationError("Enter a valid Open edX course key.") from exc

        return course_id


@admin.action(description="Enable selected courses")
def enable_courses(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """
    Enable selected auto-enroll course rows.
    """
    updated = queryset.update(enabled=True)
    modeladmin.message_user(request, f"Enabled {updated} course(s).", messages.SUCCESS)


@admin.action(description="Disable selected courses")
def disable_courses(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """
    Disable selected auto-enroll course rows.
    """
    updated = queryset.update(enabled=False)
    modeladmin.message_user(request, f"Disabled {updated} course(s).", messages.SUCCESS)


class AutoEnrollCourseAdmin(admin.ModelAdmin):
    """
    Admin controls for courses new users should be enrolled in.
    """

    form = AutoEnrollCourseForm
    list_display = ("course_id", "enrollment_mode", "enabled", "created_at", "updated_at")
    list_filter = ("enabled", "enrollment_mode")
    search_fields = ("course_id",)
    readonly_fields = ("created_at", "updated_at")
    actions = (enable_courses, disable_courses)

    def get_urls(self):
        """
        Add an admin-protected CourseOverview autocomplete endpoint.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                "course-overview-autocomplete/",
                self.admin_site.admin_view(self.course_overview_autocomplete),
                name="openedx_auto_enroll_autoenrollcourse_course_overview_autocomplete",
            ),
        ]
        return custom_urls + urls

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Render course_id as a searchable CourseOverview-backed Select2 field.
        """
        if db_field.name == "course_id":
            kwargs["widget"] = CourseOverviewAutocompleteWidget(self.admin_site)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def course_overview_autocomplete(self, request):
        """
        Return CourseOverview search results in Django admin Select2 format.
        """
        if not (
            self.has_view_permission(request)
            or self.has_add_permission(request)
            or self.has_change_permission(request)
        ):
            raise PermissionDenied

        try:
            CourseOverview = get_course_overview_model()
        except ImportError:
            return JsonResponse({"results": [], "pagination": {"more": False}})

        term = request.GET.get("term", "")
        queryset = CourseOverview.objects.all().order_by("id")
        if term:
            queryset = queryset.filter(Q(id__icontains=term) | Q(display_name__icontains=term))

        paginator = self.get_paginator(request, queryset, 20)
        page_number = request.GET.get("page", 1)
        try:
            page = paginator.page(page_number)
        except (EmptyPage, PageNotAnInteger):
            page = paginator.page(1)

        results = [
            {
                "id": str(course.id),
                "text": self.course_overview_autocomplete_label(course),
            }
            for course in page.object_list
        ]
        return JsonResponse(
            {
                "results": results,
                "pagination": {"more": page.has_next()},
            }
        )

    @staticmethod
    def course_overview_autocomplete_label(course):
        """
        Return the label shown in course autocomplete search results.
        """
        if course.display_name:
            return f"{course.id} - {course.display_name}"
        return str(course.id)


admin.site.register(AutoEnrollConfiguration, AutoEnrollConfigurationAdmin)
admin.site.register(AutoEnrollCourse, AutoEnrollCourseAdmin)
