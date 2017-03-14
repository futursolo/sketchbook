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
from . import loaders
from . import statements
from . import parser
from . import runtime
from . import printer


__all__ = ["Template"]


class Template:
    """
    A compiled, reusable template object.
    """
    def __init__(
        self, tpl_content: Union[str, bytes], *,
        path: str="<string>",
        tpl_ctx: Optional[context.TemplateContext]=None,
            loader: Optional["loaders.BaseLoader"]=None) -> None:
        self._path = path

        self._tpl_ctx = tpl_ctx or context.TemplateContext()

        self._loader = loader

        if isinstance(tpl_content, bytes):
            self._tpl_content = tpl_content.decode(
                self._tpl_ctx.source_encoding)

        else:
            self._tpl_content = tpl_content

        self._root = parser.TemplateParser.parse_tpl(self)

    @property
    def _compiled_code(self) -> CodeType:
        if not hasattr(self, "_printed_tpl"):
            self._printed_tpl = printer.CodePrinter.print_tpl(self)

        return self._printed_tpl

    def _get_namespace(
            self, tpl_globals: Mapping[str, Any]) -> runtime.TplNamespace:
        tpl_globals = tpl_globals

        exec(self._compiled_code, tpl_globals)  # type: ignore

        tpl_namespace = tpl_globals["_TplCurrentNamespace"](
            tpl=self, tpl_globals=tpl_globals)

        return tpl_namespace

    async def render(self, **kwargs: Any) -> str:
        tpl_namespace = self._get_namespace(tpl_globals=kwargs)

        await tpl_namespace._render()

        return tpl_namespace._tpl_result
