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

from typing import Optional, Mapping, Callable

from . import escaping

import asyncio
import types

__all__ = ["TemplateContext"]


class TemplateContext:
    def __init__(
        self, *, cache_tpls: bool=True,
        source_encoding: str="utf-8",
        custom_escape_fns: Mapping[str, Callable[[str], str]]={},
            loop: Optional[asyncio.AbstractEventLoop]=None) -> None:

        self._loop = loop or asyncio.get_event_loop()

        self._source_encoding = source_encoding

        escape_fns = escaping.builtin_escape_fns.copy()
        if custom_escape_fns:
            escape_fns.update(custom_escape_fns)  # type: ignore
        self._escape_fns = types.MappingProxyType(escape_fns)

        self._cache_tpls = cache_tpls

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def source_encoding(self) -> str:
        return self._source_encoding

    @property
    def escape_fns(self) -> Mapping[str, Callable[[str], str]]:
        return self._escape_fns

    @property
    def cache_tpls(self) -> bool:
        return self._cache_tpls
