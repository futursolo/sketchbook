#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2017 Kaede Hoshikawa
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from setuptools import setup, find_packages

import importlib
import os
import sys

if not sys.version_info[:3] >= (3, 6, 0):
    raise RuntimeError("Sketchbook requires Python 3.6.0 or higher.")


def load_version(module_name):
    _version_spec = importlib.util.spec_from_file_location(
        "{}._version".format(module_name),
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "{}/_version.py".format(module_name)))
    _version = importlib.util.module_from_spec(_version_spec)
    _version_spec.loader.exec_module(_version)
    return _version.version


setup_requires = ["setuptools", "pytest-runner>=2.11.1,<3"]

install_requires = ["aiofiles>=0.3.1,<1"]

tests_require = ["pytest>=3.0.7,<4"]

if __name__ == "__main__":
    setup(
        name="sketchbook",
        version=load_version("sketchbook"),
        author="Kaede Hoshikawa",
        author_email="futursolo@icloud.com",
        url="https://github.com/futursolo/sketchbook",
        license="Apache License 2.0",
        description="An ordered, one-to-many mapping.",
        long_description=open("README.rst", "r").read(),
        packages=find_packages(),
        include_package_data=True,
        setup_requires=setup_requires,
        install_requires=install_requires,
        tests_require=tests_require,
        extras_require={
            "test": tests_require
        },
        zip_safe=False,
        classifiers=[
            "Operating System :: MacOS",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Operating System :: POSIX :: Linux",
            "Operating System :: Unix",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: Implementation :: CPython"
        ]
    )
