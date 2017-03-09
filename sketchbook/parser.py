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

from typing import Optional, List

from . import statements
from . import template
from . import exceptions

import io
import re

__all__ = ["TemplateParser"]


class _ReadFinished(Exception):
    pass


class TemplateParser:
    def __init__(self, tpl: "template.Template") -> None:
        self._tpl = tpl
        self._tpl_ctx = self._tpl._tpl_ctx

        self._io = io.StringIO(self._tpl._tpl_content)

        self._current_line_no = 0
        self._current_line = ""

        self._root = statements.Root(filepath=self._tpl._path)
        self._indents: List[statements.Statement] = []

        self._parse()

    def _move_to_next_line(self) -> None:
        if self._current_line:
            raise exceptions.ParserError(
                ("Parsing of the last line is not completed "
                 "in file {} at line {}.").format(
                    self._tpl._path, self._current_line_no))

        new_line = self._io.readline()

        if not new_line:
            raise _ReadFinished

        self._current_line_no += 1
        self._current_line = new_line

    @property
    def root(self) -> statements.Root:
        return self._root

    def _parse_stmt(self, stmt_str: str) -> statements.Statement:
        raise NotImplementedError

    def _find_next_stmt(self) -> statements.Statement:
        stmt_str: List[str] = []
        begin_mark_line_no = -1

        while True:
            if not self._current_line:
                try:
                    self._move_to_next_line()

                except _ReadFinished:
                    if begin_mark_line_no != -1:
                        raise exceptions.TemplateSyntaxError(
                            ("Cannot find end mark for begin mark "
                             "in file {} at line {}.").format(
                                self._tpl._path, begin_mark_line_no))

                    elif stmt_str:
                        return statements.Plain(
                            stmt_str, filepath=self._tpl._path,
                            line_no=self._current_line_no)

    def _append_to_current(self, stmt: statements.Statement) -> None:
        if self._indents:
            self._indents[-1].append_stmt(stmt)

        else:
            self._root.append_stmt(stmt)

    def _unindent_current(self) -> None:
        if self._indents:
            self._indents.pop()

        else:
            raise exceptions.TemplateSyntaxError(
                "Redundant Unindent Statement in file {} at line {}.".format(
                    self._tpl._path, self._current_line_no))

    def _parse(self) -> None:
        while True:
            try:
                stmt = self._find_next_stmt()

            except _ReadFinished:
                break

            if stmt.should_unindent:
                self._unindent_current()

            if stmt.should_append:
                self._append_to_current(stmt)

            if stmt.should_indent:
                self._indents.append(stmt)

            if isinstance(stmt, statements.Block):
                self._root.append_block(stmt)

        if self._indents:
            raise exceptions.TemplateSyntaxError(
                "Unindented Indent Statement in file {} at line {}.".format(
                    self._tpl._path, self._indents[-1].line_no))

    @classmethod
    def parse_tpl(Cls, tpl: "template.Template") -> statements.Root:
        tpl_parser = Cls(tpl)
        return tpl_parser.root
