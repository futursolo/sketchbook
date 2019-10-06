#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2019 Kaede Hoshikawa
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

import sys

if not sys.version_info[:3] >= (3, 6, 1):
    raise RuntimeError("Sketchbook requires Python 3.6.1 or higher.")

else:
    try:
        import _modify_version

    except ImportError:
        pass

    else:
        _modify_version.modify("sketchbook")

    import _load_version

setup_requires = ["setuptools", "pytest-runner>=2.11.1,<3"]

aiofiles_requires = ["aiofiles>=0.3.1,<1"]

curio_requires = ["curio>=0.7.0,<1"]

full_requires = aiofiles_requires + curio_requires

tests_require = ["pytest>=3.0.7,<4"]
tests_require.extend(full_requires)

dev_requires = [
    "sphinx>=1.5.5,<2",
    "sphinxcontrib-asyncio>=0.2.0,<1",
    "sphinx_rtd_theme>=0.2.4,<3",
    "mypy>=0.620,<1",
    "flake8>=3.5.0,<4"]
dev_requires.extend(tests_require)

if __name__ == "__main__":
    setup(
        name="sketchbook",
        version=_load_version.load("sketchbook"),
        author="Kaede Hoshikawa",
        author_email="futursolo@icloud.com",
        url="https://github.com/futursolo/sketchbook",
        license="Apache License 2.0",
        description=("A template engine built for asyncio with "
                     "async/await syntax support."),
        long_description=open("README.rst", "r").read(),
        packages=find_packages(),
        include_package_data=True,
        setup_requires=setup_requires,
        install_requires=[],
        tests_require=tests_require,
        extras_require={
            "aiofiles": aiofiles_requires,
            "curio": curio_requires,
            "full": full_requires,
            "test": tests_require,
            "dev": dev_requires,
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
