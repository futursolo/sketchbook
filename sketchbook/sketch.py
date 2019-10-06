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

from typing import Union, Optional, Mapping, Any
from types import CodeType

from . import context
from . import parser
from . import runtime
from . import printer

import typing

if typing.TYPE_CHECKING:
    from . import finders  # noqa: F401
    from . import statements  # noqa: F401

__all__ = ["Sketch"]


class Sketch:
    """
    A compiled, reusable template object.

    :class:`.Sketch` can be initialized directly with arguments, or
    by a subclass of :class:`.BaseSketchFinder`.

    :arg __content: The content of this sketch. This can be a string or a
        bytestring. If a bytestring
        is passed, the content will be decoded with :code:`source_encoding`
        from :code:`skt_ctx`.
        This argument must be passed positionally and must be the first
        argument.
    :arg path: The path of the sketch, used by :class:`.SketchFinder` to
        resolve file relationship. Default: :code:`<string>`.
    :arg skt_ctx: The subclass of :class:`.BaseSketchContext` to be used by the
        :class:`.Sketch` Default: :code:`None`.
        (Create a new :class:`.AsyncioSketchContext` upon initialization).
    :arg finder: The finder used by the current sketch to include or inherit
        from other sketches. Default: :code:`None`.
    """
    def __init__(
        self, __content: Union[str, bytes], *,
        path: str = "<string>",
        skt_ctx: Optional["context.BaseSketchContext"] = None,
            finder: Optional["finders.BaseSketchFinder"] = None) -> None:
        self._path = path

        self._ctx = skt_ctx or context.AsyncioSketchContext()

        self._finder = finder

        if isinstance(__content, bytes):
            self._content = __content.decode(self._ctx.source_encoding)

        else:
            self._content = __content

        self._root = parser.SketchParser.parse_sketch(self)

    @property
    def _compiled_code(self) -> CodeType:
        if not hasattr(self, "_printed_skt"):
            self._printed_skt = printer.PythonPrinter.print_sketch(self)

        return self._printed_skt

    def _get_runtime(
            self, skt_globals: Mapping[str, Any]) -> runtime.SketchRuntime:
        skt_globals = skt_globals

        exec(self._compiled_code, skt_globals)  # type: ignore

        return skt_globals["_SktCurrentRuntime"](
            self, skt_globals=skt_globals)

    async def draw(self, **kwargs: Any) -> str:
        """
        Draw the sketch to :code:`str`.

        :arg \\*\\*kwargs: All the keyword arguments will become global
            variables in the runtime.

        .. warning::

            The exceptions raised in the runtime will pop up from this method.
        """
        runtime = self._get_runtime(skt_globals=kwargs)

        await runtime._draw()

        return runtime._skt_result
