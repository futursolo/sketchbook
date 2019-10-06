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

from typing import Optional, Mapping, Callable, Sequence, Type, Any

from . import escaping
from . import statements

import asyncio
import types
import abc

__all__ = [
    "BaseSketchContext", "AsyncioSketchContext"]


class BaseSketchContext(abc.ABC):
    """
    :class:`.BaseSketchContext` and its subclasses are used to configure
    :class:`.Sketch` and :class:`.BaseSketchFinder`.

    This class should be immutable after initialization.

    :arg cache_sketches: If :code:`True`, :class:`.BaseSketchFinder` will
        cache sketches. Default: :code:`True`.
    :arg source_encoding: The encoding of the source of sketches if passed
        as bytestring. Default: :code:`utf-8`.
    :arg custom_escape_fns: Dictionary containing custom escape functions.
        Functions in this dictionary will override the ones with the same name
        in the built-in escape functions. Default: :code:`{}`.

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
        self, *, cache_sketches: bool = True,
        source_encoding: str = "utf-8",
        custom_escape_fns: Mapping[str, Callable[[Any], str]] = {}
            ) -> None:

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


class AsyncioSketchContext(BaseSketchContext):
    """
    This is a subclass of :class:`.BaseSketchContext` designed to be used with
    the `asyncio <https://docs.python.org/3/library/asyncio.html>`_ module
    in the standard library.

    :arg loop: The event loop used by :class:`.Sketch` and
        :class:`.BaseSketchFinder`, must be a subclass of
        :class:`asyncio.AbstractEventLoop` or :code:`None`.
        Default: :code:`None`
        (Use the value of :func:`asyncio.get_event_loop`).
    :arg \\*\\*kwargs: This class also takes all the arguments from
        :class:`.BaseSketchContext`.
    """
    def __init__(
        self, *, cache_sketches: bool = True,
        source_encoding: str = "utf-8",
        custom_escape_fns: Mapping[str, Callable[[Any], str]] = {},
            loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        super().__init__(
            cache_sketches=cache_sketches,
            source_encoding=source_encoding,
            custom_escape_fns=custom_escape_fns)

        self._loop = loop or asyncio.get_event_loop()

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """
        Event loop used by the sketch context.
        """
        return self._loop


try:
    import curio  # noqa: F401

except ImportError:
    pass

else:
    class CurioSketchContext(BaseSketchContext):
        """
        This is a subclass of :class:`.BaseSketchContext` designed to be used
        with the `concurrent I/O <https://curio.readthedocs.io/en/latest/>`_
        library.
        """
        pass

    __all__.append("CurioSketchContext")
