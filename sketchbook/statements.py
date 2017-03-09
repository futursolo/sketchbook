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

from typing import List, Optional

from . import printer

import abc

__all__ = ["Statement", "Root", "Block"]


class Statement(abc.ABC):
    @abc.abstractmethod
    def append_stmt(self, stmt: "Statement") -> None:
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def should_indent(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def should_append(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def should_unindent(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def line_no(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        raise NotImplementedError

    @abc.abstractmethod
    def print_code(self, code_printer: printer.CodePrinter) -> None:
        raise NotImplementedError


class Root(Statement):
    def __init__(self, filepath: str) -> None:
        self._filepath = filepath

        self._stmts: List[Statement] = []

    def append_stmt(self, stmt: Statement) -> None:
        self._stmts.append(stmt)

    def append_block(self, block: "Block") -> None:
        raise NotImplementedError

    @property
    def should_indent(self) -> bool:
        raise NotImplementedError("This does not apply to Root.")

    @property
    def should_append(self) -> bool:
        raise NotImplementedError("This does not apply to Root.")

    @property
    def should_unindent(self) -> bool:
        raise NotImplementedError("This does not apply to Root.")

    @property
    def line_no(self) -> int:
        raise NotImplementedError("This does not apply to Root.")

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        raise NotImplementedError("This does not apply to Root.")

    def print_code(self, code_printer: printer.CodePrinter) -> None:
        raise NotImplementedError


class Block(Statement):
    pass


class Plain(Statement):
    pass
