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
import collections

__all__ = ["builtin_escape_fns"]


def _escape_html(unsafe_str: str) -> str:
    return html.escape(unsafe_str)


def _no_escape(unsafe_str: str) -> str:
    return unsafe_str


def _escape_url_with_plus(unsafe_str: str) -> str:
    return urllib.parse.quote_plus(unsafe_str)


def _escape_url_without_plus(unsafe_str: str) -> str:
    return urllib.parse.quote(unsafe_str)


def _escape_json(unsafe_str: str) -> str:
    return json.dumps(unsafe_str)


builtin_escape_fns = collections.OrderedDict([
    ("default", _escape_html),
    ("html", _escape_html),
    ("h", _escape_html),
    ("raw", _no_escape),
    ("r", _no_escape),
    ("url_with_plus", _escape_url_with_plus),
    ("url", _escape_url_with_plus),
    ("u", _escape_url_with_plus),
    ("url_without_plus", _escape_url_without_plus),
    ("json", _escape_json),
    ("j", _escape_json)
])
