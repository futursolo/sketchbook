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

from typing import Optional, Mapping, Callable, Sequence, Type, Any

from . import escaping
from . import statements

import asyncio
import types

__all__ = ["SketchContext"]


class SketchContext:
    """
    :class:`.SketchContext` is used to hold options for :class:`.Sketch` and
    :class:`.BaseSketchFinder`, in order to alter the default behaviours of
    them.

    This is class should be immutable after initialization.

    :arg cache_sketches: If :code:`True`, :class:`.BaseSketchFinder` will
        cache the sketches. Default: :code:`True`.
    :arg source_encoding: The encoding of the source of the sketches if passed
        as bytestring. Default: :code:`utf-8`.
    :arg custom_escape_fns: Mapping of custom escape functions. Functions in
        this mapping will override the one with the same name in the built-in
        escape functions. Default: :code:`{}`.
    :arg loop: The event loop used by :class:`.Sketch` and
        :class:`.BaseSketchFinder`, must be a subclass of
        :class:`asyncio.AbstractEventLoop` or :code:`None`.
        Default: :code:`None`
        (Use the value of :func:`asyncio.get_event_loop`).

    Built-in Escape Functions:

    - :code:`default`, :code:`h`, and :code:`html`:
        Short hand for :func:`html.escape`.
    - :code:`r` and :code:`raw`:
        Output the input with no modification.
    - :code:`j` and :code:`json`:
        Short hand for :func:`json.dumps`.
    - :code:`u`, :code:`url` and :code:`url_with_plus`:
        Short hand for :func:`urllib.parse.quote_plus`.
    - :code:`url_without_plus`:
        Short hand for :func:`urllib.parse.quote`.
    """
    def __init__(
        self, *, cache_sketches: bool=True,
        source_encoding: str="utf-8",
        custom_escape_fns: Mapping[str, Callable[[Any], str]]={},
            loop: Optional[asyncio.AbstractEventLoop]=None) -> None:

        self._loop = loop or asyncio.get_event_loop()

        self._source_encoding = source_encoding

        escape_fns = escaping.builtin_escape_fns.copy()
        if custom_escape_fns:
            escape_fns.update(custom_escape_fns)
        self._escape_fns = types.MappingProxyType(escape_fns)

        self._stmt_classes = list(statements.builtin_stmt_classes)

        class OutputStmt(statements.BaseOutput):
            _filter_fn_names = list(self.escape_fns.keys())

        self._stmt_classes.append(OutputStmt)

        self._cache_sketches = cache_sketches

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def source_encoding(self) -> str:
        return self._source_encoding

    @property
    def escape_fns(self) -> Mapping[str, Callable[[Any], str]]:
        return self._escape_fns

    @property
    def stmt_classes(self) -> Sequence[Type[statements.Statement]]:
        return self._stmt_classes

    @property
    def cache_sketches(self) -> bool:
        return self._cache_sketches
