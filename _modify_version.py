#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2018 Kaede Hoshikawa
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

import os
import re

_DEV_RE = re.compile(r"_dev\s*?=\s*?.*", flags=re.M)


def modify(project_folder: str) -> None:
    tag = os.environ.get("TRAVIS_TAG", None)

    if tag:
        dev_no = "None"

    else:
        dev_no = str(os.environ.get("TRAVIS_BUILD_NUMBER", "0"))

    with open(f"{project_folder}/_version.py", "r+") as f:
        f_str = f.read()
        f_str = re.sub(_DEV_RE, f"_dev = {dev_no}", f_str)

        f.seek(0)
        f.truncate()
        f.write(f_str)
        f.flush()
