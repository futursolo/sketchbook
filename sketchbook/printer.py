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

from typing import Any, Optional
from types import CodeType

import typing

if typing.TYPE_CHECKING:
    from . import sketch  # noqa: F401
    from . import statements  # noqa: F401

__all__ = ["PythonPrinter"]


class PythonPrinter:
    """
    Print Python code with indentation gracefully.
    """
    def __init__(
        self, path: str = "<string>", end: str = "\n",
            indent_mark: str = " " * 4) -> None:
        self._path = path
        self._indent_num = 0
        self._committed_code = ""

        self._end = end
        self._indent_mark = indent_mark

        self._finished = False

    def writeline(
        self, line: str,
            stmt: Optional["statements.AppendMixIn"] = None) -> None:
        """
        Write a line with indent.
        """
        assert not self._finished, "Code Generation has already been finished."

        if stmt:
            line += f"  # in file {self._path} at line {stmt.line_no}."

        final_line = self._indent_mark * self._indent_num + line + self._end
        self._committed_code += final_line

    def indent_block(self) -> "PythonPrinter":
        """
        Indent the code with `with` statement.

        Example::

              printer.writeline("def a():")
              with printer.indent_block():
                  printer.writeline("return \"Text from function a.\"")

              printer.writeline("a()")

        """
        assert not self._finished, "Code Generation has already been finished."
        return self

    def _inc_indent_num(self) -> None:
        assert not self._finished, "Code Generation has already been finished."
        self._indent_num += 1

    def _dec_indent_num(self) -> None:
        assert not self._finished, "Code Generation has already been finished."
        self.writeline("pass")
        self._indent_num -= 1

    def __enter__(self) -> None:
        self._inc_indent_num()

    def __exit__(self, *exc: Any) -> None:
        self._dec_indent_num()

    @property
    def finished(self) -> bool:  # pragma: no cover
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
        Return compiled code.
        """
        if not hasattr(self, "_compiled_code"):
            self._compiled_code = compile(
                self.plain_code, self._path, "exec", dont_inherit=True)

        return self._compiled_code

    @classmethod
    def print_sketch(Cls, skt: "sketch.Sketch") -> CodeType:
        py_printer = Cls(path=skt._path)
        skt._root.print_code(py_printer)
        return py_printer.compiled_code
