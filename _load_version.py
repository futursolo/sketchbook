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

import importlib.util
import os


def load(project_folder: str) -> str:
    _version_spec = importlib.util.spec_from_file_location(
        f"{project_folder}._version",
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"{project_folder}/_version.py"))

    _version = importlib.util.module_from_spec(_version_spec)
    _version_spec.loader.exec_module(_version)

    return _version.__version__
