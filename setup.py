#!/usr/bin/env python
"""
Package metadata for openedx_auto_enroll.
"""

import os
import re
import sys

from setuptools import setup


def get_version(*file_paths):
    """
    Extract the version string from the package.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename, encoding="utf8").read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def load_requirements(*requirements_paths):
    """
    Load package requirements from requirements files.
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.split("#")[0].strip()
            for line in open(path, encoding="utf8").readlines()
            if is_requirement(line.strip())
        )
    return list(requirements)


def is_requirement(line):
    """
    Return True when a requirements line names an installable package.
    """
    return line and not line.startswith(("-r", "#", "-e", "git+", "-c"))


VERSION = get_version("openedx_auto_enroll", "__init__.py")

if sys.argv[-1] == "tag":
    print("Tagging the version on github:")
    os.system(f"git tag -a {VERSION} -m 'version {VERSION}'")
    os.system("git push --tags")
    sys.exit()

README = open(os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf8").read()
CHANGELOG = open(os.path.join(os.path.dirname(__file__), "CHANGELOG.rst"), encoding="utf8").read()

setup(
    name="openedx-auto-enroll",
    version=VERSION,
    description="Open edX plugin for automatically enrolling new users in admin-selected courses.",
    long_description=README + "\n\n" + CHANGELOG,
    author="Abstract Technology",
    url="https://github.com/Abstract-Tech/openedx-auto-enroll",
    packages=[
        "openedx_auto_enroll",
        "openedx_auto_enroll.migrations",
        "openedx_auto_enroll.settings",
        "openedx_auto_enroll.tests",
    ],
    include_package_data=True,
    install_requires=load_requirements("requirements/base.in"),
    python_requires=">=3.11",
    license="AGPL 3.0",
    zip_safe=False,
    keywords="Python edx openedx auto enroll",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "lms.djangoapp": [
            "openedx_auto_enroll = openedx_auto_enroll.apps:OpenedxAutoEnrollConfig",
        ],
    },
)
