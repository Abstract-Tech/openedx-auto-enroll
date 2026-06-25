"""
Sphinx configuration for Open edX Auto Enroll.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openedx_auto_enroll.settings.test")

import django  # pylint: disable=wrong-import-position

django.setup()

project = "Open edX Auto Enroll"
copyright = "2026, Abstract Technology"
author = "Abstract Technology"
release = "latest"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/Abstract-Tech/openedx-auto-enroll",
    "repository_branch": "main",
    "path_to_docs": "docs/",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
}
html_logo = "https://logos.openedx.org/open-edx-logo-color.png"
html_favicon = "https://logos.openedx.org/open-edx-favicon.ico"
html_static_path = ["_static"]
