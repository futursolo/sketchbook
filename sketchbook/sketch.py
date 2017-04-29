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

from typing import Union, Optional, Mapping, Any
from types import CodeType

from . import context
from . import finders
from . import statements
from . import parser
from . import runtime
from . import printer


__all__ = ["Sketch"]


class Sketch:
    """
    A compiled, reusable template object.
    """
    def __init__(
        self, __content: Union[str, bytes], *,
        path: str="<string>",
        skt_ctx: Optional["context.SketchContext"]=None,
            finder: Optional["finders.BaseSketchFinder"]=None) -> None:
        self._path = path

        self._ctx = skt_ctx or context.SketchContext()

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
        runtime = self._get_runtime(skt_globals=kwargs)

        await runtime._draw()

        return runtime._skt_result
