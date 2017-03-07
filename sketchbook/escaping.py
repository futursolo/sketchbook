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

import html
import urllib.parse
import functools
import json


def escape_html(unsafe_str: str) -> str:
    return html.escape(unsafe_str)


def no_escape(unsafe_str: str) -> str:
    return unsafe_str


def escape_url_with_plus(unsafe_str: str) -> str:
    return urllib.parse.quote_plus(unsafe_str)


def escape_url_without_plus(unsafe_str: str) -> str:
    return urllib.parse.quote(unsafe_str)


def escape_json(unsafe_str: str) -> str:
    return json.dumps(unsafe_str)


builtin_escape_fns = {
    "default": escape_html,
    "html": escape_html,
    "h": escape_html,
    "raw": no_escape,
    "r": no_escape,
    "url_with_plus": escape_url_with_plus,
    "url": escape_url_with_plus,
    "u": escape_url_with_plus,
    "url_without_plus": escape_url_without_plus,
    "json": escape_json,
    "j": escape_json
}
