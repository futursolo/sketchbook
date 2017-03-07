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

from typing import Optional

import asyncio

__all__ = ["TemplateContext"]


class TemplateContext:
    def __init__(
        self, *, cache_tpls: bool=True, default_escape: str="html",
        source_encoding: str="utf-8", output_encoding: str="utf-8",
        escape_url_with_plus: bool=True,
            loop: Optional[asyncio.AbstractEventLoop]=None) -> None:

        self._loop = loop or asyncio.get_event_loop()

        self._default_escape = default_escape
        self._source_encoding = source_encoding
        self._output_encoding = output_encoding
        self._escape_url_with_plus = escape_url_with_plus

        self._cache_tpls = cache_tpls

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def default_escape(self) -> str:
        return self._default_escape

    @property
    def source_encoding(self) -> str:
        return self._source_encoding

    @property
    def output_encoding(self) -> str:
        return self.output_encoding

    @property
    def escape_url_with_plus(self) -> bool:
        return self._escape_url_with_plus

    @property
    def cache_tpls(self) -> bool:
        return self._cache_tpls
