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

from typing import Any
from types import CodeType

__all__ = ["CodePrinter"]


class CodePrinter:
    """
    Print Python code with indentation gracefully.
    """
    def __init__(
        self, path: str="<string>", end: str="\n",
            indent_mark: str=" " * 4) -> None:
        self._path = path
        self._indent_num = 0
        self._committed_code = ""

        self._end = end
        self._indent_mark = indent_mark

        self._finished = False

    def writeline(self, line: str) -> None:
        """
        Write a line with indent.
        """
        assert not self._finished, "Code Generation has already been finished."

        final_line = self._indent_mark * self._indent_num + line + self._end
        self._committed_code += final_line

    def indent_block(self, indent_line: str) -> "CodePrinter":
        """
        Indent the code with `with` statement.

        Example:
        ..code-block:: python3

            with printer.indent_block("def a()"):
                printer.writeline("return \"Text from function a.\"")

            printer.writeline("a()")
        """
        assert not self._finished, "Code Generation has already been finished."
        self.writeline(indent_line + ":")
        return self

    def _inc_indent_num(self) -> None:
        assert not self._finished, "Code Generation has already been finished."
        self._indent_num += 1

    def _dec_indent_num(self) -> None:
        assert not self._finished, "Code Generation has already been finished."
        self._indent_num -= 1

    def __enter__(self) -> None:
        self._inc_indent_num()

    def __exit__(self, *exc: Any) -> None:
        self._dec_indent_num()

    @property
    def finished(self) -> bool:
        return self._finished

    @property
    def plain_code(self) -> str:
        """
        Return the plain, printed code.
        """
        self._finished = True
        return self._committed_code

    @property
    def compiled_code(self) -> CodeType:
        """
        Return the compiled code.
        """
        if not hasattr(self, "_compiled_code"):
            self._compiled_code = compile(
                self.plain_code, self._path, "exec", dont_inherit=True)

        return self._compiled_code
